"""
Automated PowerPoint Presentation Generator (Phase 8).

Generates 100% valid, editable OOXML Microsoft PowerPoint (.pptx) presentations
using pure Python (zipfile + XML), requiring zero external C-extensions or packages.
Compatible with Microsoft PowerPoint, Google Slides, Apple Keynote, and LibreOffice Impress.
"""

import os
import io
import zipfile
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional


def _escape_xml(text: str) -> str:
    """Escape XML special characters."""
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


class PresentationGenerator:
    """Generates a professional 10-slide capstone / hackathon presentation."""

    SLIDE_WIDTH = 9144000   # 10 inches (standard 4:3 or widescreen 16:9 EMU)
    SLIDE_HEIGHT = 6858000  # 7.5 inches EMU

    @classmethod
    def generate_project_pptx(cls, project_data: Dict[str, Any]) -> bytes:
        """
        Build a 10-slide editable .pptx presentation:
        1. Title
        2. Problem Statement
        3. Proposed Solution
        4. Objectives
        5. System Architecture
        6. Technology Stack
        7. Main Modules
        8. Implementation Workflow
        9. Expected Results
        10. Conclusion and Future Scope
        """
        title = project_data.get("title", "AI Project & Hackathon Co-Pilot")
        domain = project_data.get("domain", "AI / Machine Learning")
        author = project_data.get("author", "Student Engineering Team")
        institution = project_data.get("institution", "National Engineering Institute")

        analysis = project_data.get("analysis", {})
        tech_stack = project_data.get("technology_stack", {})
        architecture = project_data.get("architecture", {})
        roadmap = project_data.get("roadmap", {})

        slides_content = [
            # Slide 1: Title
            {
                "title": title,
                "subtitle": f"Final-Year Engineering Capstone Defense\nDomain: {domain}\nPresented by: {author}\n{institution}",
                "bullets": [],
            },
            # Slide 2: Problem Statement
            {
                "title": "Problem Statement & Background",
                "subtitle": "Current Challenges & Industry Gaps",
                "bullets": [
                    analysis.get("problem_statement", "Real-world engineering challenges lack automated detection and decision support."),
                    "High human operational cost and delay in identifying critical events.",
                    "Existing limitations: " + (", ".join(analysis.get("existing_limitations", ["Manual monitoring is slow", "Limited coverage"]))[:150]),
                    f"Target User Personas: {', '.join(analysis.get('target_users', ['Engineering Teams', 'System Operators']))}",
                ],
            },
            # Slide 3: Proposed Solution
            {
                "title": "Proposed Solution & Innovation",
                "subtitle": "Autonomous Multi-Agent Architecture",
                "bullets": [
                    analysis.get("proposed_solution", "An end-to-end intelligent system automating data ingestion, inference, and alert dispatch."),
                    f"Unique Selling Proposition (USP): {analysis.get('unique_selling_proposition', 'Real-time multi-agent orchestration with zero cloud credit waste.')}",
                    "Core Innovation: Free-first tooling, modular decoupled microservices, and rapid verification.",
                    "Provides instant feedback, actionable telemetry, and verifiable system integrity.",
                ],
            },
            # Slide 4: Objectives
            {
                "title": "Core Engineering Objectives",
                "subtitle": "Measurable Milestones for Capstone Evaluation",
                "bullets": analysis.get("main_objectives", [
                    "Design and implement scalable REST APIs with FastAPI.",
                    "Integrate real-time computer vision / machine learning pipeline.",
                    "Build responsive React frontend for live dashboard visualization.",
                    "Achieve 80%+ test coverage across unit and integration suites.",
                    "Ensure IEEE-aligned documentation and reproducible local execution.",
                ])[:5],
            },
            # Slide 5: System Architecture
            {
                "title": "System Architecture & Topology",
                "subtitle": "Decoupled 3-Tier Distributed Architecture",
                "bullets": [
                    f"Pattern: {architecture.get('architecture_pattern', 'Modular Monolith / Microservices')}",
                    f"Frontend: {architecture.get('frontend_layer', 'React 19 + TypeScript + Tailwind CSS')}",
                    f"Backend Layer: {architecture.get('backend_layer', 'FastAPI Async REST Server with Uvicorn')}",
                    f"Data Layer: {architecture.get('data_layer', 'PostgreSQL / SQLite with relational ACID transactions')}",
                    f"Agent Layer: {architecture.get('ai_pipeline_layer', 'LangGraph Supervisor Orchestration with 14 specialized agents')}",
                ],
            },
            # Slide 6: Technology Stack
            {
                "title": "Technology Stack & Tooling",
                "subtitle": "Prioritizing Free and Open-Source Technologies",
                "bullets": [
                    "Backend: Python 3.10+, FastAPI, Pydantic v2, Uvicorn",
                    "Frontend: React 19, TypeScript, Tailwind CSS v4, Vite",
                    "AI / LLM Layer: Anthropic Claude 3.5 Sonnet API + LangGraph StateGraph",
                    "Testing & QA: pytest, pytest-asyncio, HTTPX AsyncClient",
                    "Database & Security: SQLite / PostgreSQL, PBKDF2 Hashing, RFC 7519 JWT",
                ],
            },
            # Slide 7: Main Modules
            {
                "title": "Key System Modules",
                "subtitle": "Component Breakdown & Responsibilities",
                "bullets": [
                    "Module 1: Ingestion & Preprocessing (RTSP Video Feeds / API Payloads)",
                    "Module 2: AI Intelligence Engine (Inference models & Supervisor Routing)",
                    "Module 3: Project Guidance Engine (Feasibility analysis & Free tech stack)",
                    "Module 4: Hackathon Strategy Engine (MoSCoW MVP scoping & Pitch scripts)",
                    "Module 5: Workspace & Presentation Generator (Tasks & PPTX exporter)",
                ],
            },
            # Slide 8: Implementation Workflow
            {
                "title": "Implementation & Development Roadmap",
                "subtitle": "9-Phase Engineering Schedule",
                "bullets": [
                    "Phase 1-2: Core Environment, REST Health Check, Claude API Integration (Weeks 1-2)",
                    "Phase 3-4: Project Guidance & Hackathon Guidance Domain Services (Weeks 3-5)",
                    "Phase 5-6: LangGraph Multi-Agent Engine & React SaaS Dashboard (Weeks 6-8)",
                    "Phase 7-8: Database Persistence, JWT Auth, and Automated PowerPoint Generator (Weeks 9-10)",
                    "Phase 9-10: End-to-End Regression Testing, Security Review, and Deployment (Weeks 11-12)",
                ],
            },
            # Slide 9: Expected Results
            {
                "title": "Expected Outcomes & Experimental Results",
                "subtitle": "Verification Metrics and Performance Targets",
                "bullets": analysis.get("expected_outcomes", [
                    "Sub-100ms API response latency on local development servers.",
                    "Zero paid API credit leakage during testing via deterministic fixtures.",
                    "Full test suite pass rate: 62+ automated tests passing 100%.",
                    "Seamless cross-platform deployment on standard developer workstations.",
                    "Presentation decks and IEEE report generated with a single click.",
                ])[:5],
            },
            # Slide 10: Conclusion & Future Scope
            {
                "title": "Conclusion & Future Enhancements",
                "subtitle": "Capstone Defense Summary",
                "bullets": [
                    "Successfully delivered an end-to-end AI Co-Pilot for engineering students.",
                    "Eliminated the guesswork in technology selection and hackathon MVP scoping.",
                    "Future Scope 1: WebRTC real-time low-latency video streaming.",
                    "Future Scope 2: Fine-tuned local SLM (e.g. Llama 3) for 100% offline edge inference.",
                    "Thank You! Questions & Discussion.",
                ],
            },
        ]

        return cls._create_ooxml_package(slides_content)

    @classmethod
    def _create_ooxml_package(cls, slides: List[Dict[str, Any]]) -> bytes:
        """Create a complete ZIP archive matching Microsoft PowerPoint OOXML specs."""
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            # 1. [Content_Types].xml
            zf.writestr("[Content_Types].xml", cls._get_content_types_xml(len(slides)))

            # 2. _rels/.rels
            zf.writestr("_rels/.rels", cls._get_global_rels_xml())

            # 3. ppt/presentation.xml
            zf.writestr("ppt/presentation.xml", cls._get_presentation_xml(len(slides)))

            # 4. ppt/_rels/presentation.xml.rels
            zf.writestr("ppt/_rels/presentation.xml.rels", cls._get_presentation_rels_xml(len(slides)))

            # 5. Slides
            for i, slide in enumerate(slides, start=1):
                zf.writestr(f"ppt/slides/slide{i}.xml", cls._get_slide_xml(slide, i))
                zf.writestr(f"ppt/slides/_rels/slide{i}.xml.rels", cls._get_slide_rels_xml())

            # 6. Slide Layout & Master
            zf.writestr("ppt/slideLayouts/slideLayout1.xml", cls._get_slide_layout_xml())
            zf.writestr("ppt/slideLayouts/_rels/slideLayout1.xml.rels", cls._get_slide_layout_rels_xml())
            zf.writestr("ppt/slideMasters/slideMaster1.xml", cls._get_slide_master_xml())
            zf.writestr("ppt/slideMasters/_rels/slideMaster1.xml.rels", cls._get_slide_master_rels_xml())
            zf.writestr("ppt/theme/theme1.xml", cls._get_theme_xml())

        buf.seek(0)
        return buf.getvalue()

    @staticmethod
    def _get_content_types_xml(num_slides: int) -> str:
        slide_overrides = "".join([
            f'<Override PartName="/ppt/slides/slide{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
            for i in range(1, num_slides + 1)
        ])
        return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
    <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
    <Default Extension="xml" ContentType="application/xml"/>
    <Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>
    <Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>
    <Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>
    <Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>
    {slide_overrides}
</Types>"""

    @staticmethod
    def _get_global_rels_xml() -> str:
        return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
    <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>
</Relationships>"""

    @staticmethod
    def _get_presentation_xml(num_slides: int) -> str:
        slide_ids = "".join([
            f'<p:sldId id="{255 + i}" r:id="rId{i}"/>'
            for i in range(1, num_slides + 1)
        ])
        return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
                xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
                xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
    <p:sldMasterIdLst>
        <p:sldMasterId id="2147483648" r:id="rIdMaster1"/>
    </p:sldMasterIdLst>
    <p:sldIdLst>
        {slide_ids}
    </p:sldIdLst>
    <p:sldSz cx="9144000" cy="6858000" type="screen4x3"/>
    <p:notesSz cx="6858000" cy="9144000"/>
</p:presentation>"""

    @staticmethod
    def _get_presentation_rels_xml(num_slides: int) -> str:
        slide_rels = "".join([
            f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{i}.xml"/>'
            for i in range(1, num_slides + 1)
        ])
        return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
    <Relationship Id="rIdMaster1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>
    {slide_rels}
</Relationships>"""

    @classmethod
    def _get_slide_xml(cls, slide_data: Dict[str, Any], slide_num: int) -> str:
        title = _escape_xml(slide_data.get("title", ""))
        subtitle = _escape_xml(slide_data.get("subtitle", ""))
        bullets = slide_data.get("bullets", [])

        # Format bullet list
        bullet_xml = ""
        for b in bullets:
            bullet_xml += f"""
            <a:p>
                <a:pPr lvl="0">
                    <a:buChar char="•"/>
                </a:pPr>
                <a:r>
                    <a:rPr lang="en-US" sz="1800">
                        <a:solidFill><a:srgbClr val="334155"/></a:solidFill>
                    </a:rPr>
                    <a:t>{_escape_xml(b)}</a:t>
                </a:r>
            </a:p>"""

        return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
       xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
       xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
    <p:cSld>
        <p:spTree>
            <p:nvGrpSpPr>
                <p:cNvPr id="1" name=""/>
                <p:cNvGrpSpPr/>
                <p:nvPr/>
            </p:nvGrpSpPr>
            <p:grpSpPr>
                <a:xfrm>
                    <a:off x="0" y="0"/>
                    <a:ext cx="0" cy="0"/>
                    <a:chOff x="0" y="0"/>
                    <a:chExt cx="0" cy="0"/>
                </a:xfrm>
            </p:grpSpPr>

            <!-- Slide Title Shape -->
            <p:sp>
                <p:nvSpPr>
                    <p:cNvPr id="2" name="Title Shape"/>
                    <p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>
                    <p:nvPr/>
                </p:nvSpPr>
                <p:spPr>
                    <a:xfrm>
                        <a:off x="457200" y="457200"/>
                        <a:ext cx="8229600" cy="1143000"/>
                    </a:xfrm>
                    <a:solidFill><a:srgbClr val="0F172A"/></a:solidFill>
                    <a:roundRect rx="80000"/>
                </p:spPr>
                <p:txBody>
                    <a:bodyPr vert="horz" lIns="180000" tIns="140000" rIns="180000" bIns="140000"/>
                    <a:lstStyle/>
                    <a:p>
                        <a:r>
                            <a:rPr lang="en-US" sz="2800" b="1">
                                <a:solidFill><a:srgbClr val="38BDF8"/></a:solidFill>
                            </a:rPr>
                            <a:t>{title}</a:t>
                        </a:r>
                    </a:p>
                    <a:p>
                        <a:r>
                            <a:rPr lang="en-US" sz="1400" i="1">
                                <a:solidFill><a:srgbClr val="94A3B8"/></a:solidFill>
                            </a:rPr>
                            <a:t>{subtitle}</a:t>
                        </a:r>
                    </a:p>
                </p:txBody>
            </p:sp>

            <!-- Content / Bullets Shape -->
            <p:sp>
                <p:nvSpPr>
                    <p:cNvPr id="3" name="Content Shape"/>
                    <p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>
                    <p:nvPr/>
                </p:nvSpPr>
                <p:spPr>
                    <a:xfrm>
                        <a:off x="457200" y="1828800"/>
                        <a:ext cx="8229600" cy="4572000"/>
                    </a:xfrm>
                    <a:solidFill><a:srgbClr val="F8FAFC"/></a:solidFill>
                    <a:ln w="12700"><a:solidFill><a:srgbClr val="E2E8F0"/></a:solidFill></a:ln>
                    <a:roundRect rx="80000"/>
                </p:spPr>
                <p:txBody>
                    <a:bodyPr vert="horz" lIns="250000" tIns="250000" rIns="250000" bIns="250000"/>
                    <a:lstStyle/>
                    {bullet_xml}
                </p:txBody>
            </p:sp>
        </p:spTree>
    </p:cSld>
    <p:clrMapOvr>
        <a:masterClrMapping/>
    </p:clrMapOvr>
</p:sld>"""

    @staticmethod
    def _get_slide_rels_xml() -> str:
        return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
    <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
</Relationships>"""

    @staticmethod
    def _get_slide_layout_xml() -> str:
        return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldLayout xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
             xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
             xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
             type="blank" preserve="1">
    <p:cSld name="Blank Layout">
        <p:spTree>
            <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
            <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
        </p:spTree>
    </p:cSld>
    <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sldLayout>"""

    @staticmethod
    def _get_slide_layout_rels_xml() -> str:
        return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
    <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="../slideMasters/slideMaster1.xml"/>
</Relationships>"""

    @staticmethod
    def _get_slide_master_xml() -> str:
        return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldMaster xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
             xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
             xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
    <p:cSld>
        <p:spTree>
            <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
            <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
        </p:spTree>
    </p:cSld>
    <p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/>
    <p:sldLayoutIdLst>
        <p:sldLayoutId id="2147483649" r:id="rIdLayout1"/>
    </p:sldLayoutIdLst>
</p:sldMaster>"""

    @staticmethod
    def _get_slide_master_rels_xml() -> str:
        return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
    <Relationship Id="rIdLayout1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
    <Relationship Id="rIdTheme1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="../theme/theme1.xml"/>
</Relationships>"""

    @staticmethod
    def _get_theme_xml() -> str:
        return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="Office Theme">
    <a:themeElements>
        <a:clrScheme name="Office">
            <a:dk1><a:sysClr val="windowText" lastClr="000000"/></a:dk1>
            <a:lt1><a:sysClr val="window" lastClr="FFFFFF"/></a:lt1>
            <a:dk2><a:srgbClr val="1E293B"/></a:dk2>
            <a:lt2><a:srgbClr val="F8FAFC"/></a:lt2>
            <a:accent1><a:srgbClr val="2563EB"/></a:accent1>
            <a:accent2><a:srgbClr val="7C3AED"/></a:accent2>
            <a:accent3><a:srgbClr val="059669"/></a:accent3>
            <a:accent4><a:srgbClr val="D97706"/></a:accent4>
            <a:accent5><a:srgbClr val="DC2626"/></a:accent5>
            <a:accent6><a:srgbClr val="0284C7"/></a:accent6>
            <a:hlink><a:srgbClr val="2563EB"/></a:hlink>
            <a:folHlink><a:srgbClr val="7C3AED"/></a:folHlink>
        </a:clrScheme>
        <a:fontScheme name="Office">
            <a:majorFont><a:latin typeface="Calibri"/></a:majorFont>
            <a:minorFont><a:latin typeface="Calibri"/></a:minorFont>
        </a:fontScheme>
        <a:fmtScheme name="Office">
            <a:fillStyleLst><a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill></a:fillStyleLst>
            <a:lnStyleLst><a:ln w="9525"><a:solidFill><a:srgbClr val="000000"/></a:solidFill></a:ln></a:lnStyleLst>
            <a:effectStyleLst><a:effectStyle><a:effectLst/></a:effectStyle></a:effectStyleLst>
            <a:bgFillStyleLst><a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill></a:bgFillStyleLst>
        </a:fmtScheme>
    </a:themeElements>
</a:theme>"""
