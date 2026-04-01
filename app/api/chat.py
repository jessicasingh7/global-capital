"""Chat API — answers questions about global capital using Claude + data context."""

import json
import os
from pathlib import Path
from fastapi import APIRouter, Request
from typing import Optional
from pydantic import BaseModel
import anthropic

router = APIRouter()

DATA_DIR = Path(__file__).resolve().parent.parent.parent / 'data'

client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))


def load_context():
    """Load all data files as context for Claude."""
    context_parts = []

    # Globe data (country-level capital breakdown)
    globe_path = DATA_DIR / 'globe_total.json'
    if globe_path.exists():
        with open(globe_path) as f:
            data = json.load(f)
        context_parts.append("## Country Capital Data (current)\n")
        for c in data:
            parts = [f"**{c['country_name']}** ({c['country_code']})"]
            parts.append(f"Total: ${c['total_capital_usd']/1e12:.1f}T")
            if c.get('population'):
                parts.append(f"Pop: {c['population']/1e6:.0f}M")
                parts.append(f"Per capita: ${c['total_capital_usd']/c['population']:,.0f}")
            if c.get('gdp_usd'):
                parts.append(f"GDP: ${c['gdp_usd']/1e12:.1f}T")
            bd = c.get('breakdown', {})
            breakdown_str = ', '.join(f"{k}: ${v/1e12:.1f}T" for k, v in sorted(bd.items(), key=lambda x: -x[1]) if v > 0)
            parts.append(f"Breakdown: {breakdown_str}")
            if c.get('top_companies'):
                cos = ', '.join(f"{co['name']} (${co['market_cap']/1e9:.0f}B)" for co in c['top_companies'][:3])
                parts.append(f"Top companies: {cos}")
            if c.get('top_billionaires'):
                bills = ', '.join(f"{b['name']} ${b['worth']/1e9:.0f}B" for b in c['top_billionaires'][:3])
                parts.append(f"Top billionaires: {bills}")
            if c.get('vc_stats'):
                vc = c['vc_stats']
                parts.append(f"VC: ${vc['total_annual_usd']/1e9:.0f}B/yr, {vc['num_deals']} deals, sectors: {', '.join(vc['top_sectors'][:3])}")
            context_parts.append(' | '.join(parts))

    # Sector flows
    sf_path = DATA_DIR / 'sector_flows.json'
    if sf_path.exists():
        with open(sf_path) as f:
            sf = json.load(f)
        context_parts.append("\n## VC Funding by Sector (2025)")
        for s in sf.get('vc_by_sector', {}).get('flows', []):
            context_parts.append(f"- {s['name']}: ${s['amount']/1e9:.0f}B ({'+' if s['change']>=0 else ''}{s['change']}% YoY)")
        context_parts.append("\n## Money Migration Trends (2020-2025)")
        for s in sf.get('money_migration', {}).get('shifts', []):
            context_parts.append(f"- {s['from']} → {s['to']}: ${s['amount']/1e9:.0f}B — {s['context']}")

    # Scale totals
    scale_path = DATA_DIR / 'scale_totals.json'
    if scale_path.exists():
        with open(scale_path) as f:
            scale = json.load(f)
        context_parts.append("\n## Global Asset Class Totals")
        for a in scale.get('asset_classes', []):
            context_parts.append(f"- {a['name']}: ${a['total_usd']/1e12:.1f}T")

    return '\n'.join(context_parts)


SYSTEM_PROMPT = """You are a global capital markets analyst embedded in an interactive visualization of all the world's capital. You have access to current data on every major country's assets, companies, billionaires, VC activity, and capital flows.

Your role:
- Answer questions about where money is, how it flows, and what's changing
- Reference specific numbers from the data provided
- Make comparisons that help people understand scale ("X's wealth equals Y country's entire GDP")
- Be concise but insightful — 2-4 paragraphs max
- If someone asks about investing, give educational context about where capital is concentrated, not financial advice
- Highlight surprising or non-obvious insights
- Use $ formatting with B/T suffixes

You are speaking to a general audience, not finance professionals. Make it accessible."""


class ChatRequest(BaseModel):
    message: str
    country_code: Optional[str] = None


class ChatResponse(BaseModel):
    response: str


@router.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    context = load_context()

    # If a country is selected, add emphasis
    country_note = ""
    if req.country_code:
        country_note = f"\n\nThe user is currently viewing {req.country_code} on the globe. Prioritize information about this country in your response if relevant."

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=800,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"Here is the current global capital data:\n\n{context}{country_note}\n\nUser question: {req.message}"
            }
        ]
    )

    return ChatResponse(response=message.content[0].text)
