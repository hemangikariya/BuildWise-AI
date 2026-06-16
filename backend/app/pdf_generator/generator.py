import os
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from app.core.config import settings
from app.core.logging import system_logger
from app.models.project import ProjectVersion, Project
from app.models.rag import Report

# Directory for storing generated reports
REPORTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "reports"))
os.makedirs(REPORTS_DIR, exist_ok=True)

class NumberedCanvas(canvas.Canvas):
    """Custom canvas to generate 'Page X of Y' page numbers dynamically."""
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_elements(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_elements(self, page_count):
        # Suppress headers and footers on the cover page (page 1)
        if self._pageNumber == 1:
            return

        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#334155"))  # Charcoal

        # Header
        self.drawString(54, 750, "BUILDWISE AI — ENTERPRISE CTO REPORT")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))  # Light grey line
        self.setLineWidth(0.5)
        self.line(54, 742, 558, 742)

        # Footer
        self.line(54, 55, 558, 55)
        self.drawString(54, 42, f"Prepared for project version reference: {datetime.utcnow().strftime('%Y-%m-%d')}")
        self.drawRightString(558, 42, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()

class PDFReportBuilder:
    def generate_report(self, db: Session, version_id: str) -> str:
        """Collects project data and builds a professional consultant-grade PDF report."""
        version = db.query(ProjectVersion).filter(ProjectVersion.id == uuid.UUID(version_id)).first()
        if not version:
            raise ValueError(f"ProjectVersion {version_id} not found.")

        project = db.query(Project).filter(Project.id == version.project_id).first()
        project_title = project.title if project else "BuildWise AI Project"
        
        pdf_filename = f"CTO_Report_{version_id}_{int(datetime.utcnow().timestamp())}.pdf"
        pdf_path = os.path.join(REPORTS_DIR, pdf_filename)
        
        system_logger.info(f"Generating PDF Report: {pdf_path}")
        
        # Setup document
        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=letter,
            rightMargin=54,
            leftMargin=54,
            topMargin=72,
            bottomMargin=72
        )
        
        # Styles
        styles = getSampleStyleSheet()
        
        # Color definitions
        PRIMARY_COLOR = colors.HexColor("#1E3A8A")   # Dark Navy
        SECONDARY_COLOR = colors.HexColor("#0D9488") # Teal
        TEXT_COLOR = colors.HexColor("#1E293B")      # Slate 800
        
        # Custom Typography Styles
        title_style = ParagraphStyle(
            'CoverTitle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=32,
            leading=38,
            textColor=PRIMARY_COLOR,
            alignment=1, # Centered
            spaceAfter=15
        )
        
        subtitle_style = ParagraphStyle(
            'CoverSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=16,
            leading=22,
            textColor=SECONDARY_COLOR,
            alignment=1,
            spaceAfter=40
        )
        
        meta_style = ParagraphStyle(
            'CoverMeta',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            leading=14,
            textColor=TEXT_COLOR,
            alignment=1
        )
        
        h1_style = ParagraphStyle(
            'ReportH1',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=18,
            leading=22,
            textColor=PRIMARY_COLOR,
            spaceBefore=15,
            spaceAfter=10,
            keepWithNext=True
        )
        
        h2_style = ParagraphStyle(
            'ReportH2',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=13,
            leading=17,
            textColor=SECONDARY_COLOR,
            spaceBefore=10,
            spaceAfter=5,
            keepWithNext=True
        )
        
        body_style = ParagraphStyle(
            'ReportBody',
            parent=styles['BodyText'],
            fontName='Helvetica',
            fontSize=10,
            leading=15,
            textColor=TEXT_COLOR,
            spaceAfter=8
        )
        
        story = []
        
        # --- COVER PAGE ---
        story.append(Spacer(1, 150))
        story.append(Paragraph("BUILDWISE AI", title_style))
        story.append(Paragraph("AI CTO PLATFORM POWERED BY AGENTIC AI", subtitle_style))
        story.append(Spacer(1, 30))
        story.append(Paragraph(f"<b>Technical Blueprint:</b> {project_title}", subtitle_style))
        story.append(Spacer(1, 100))
        
        story.append(Paragraph(f"<b>Generated On:</b> {datetime.utcnow().strftime('%B %d, %Y')}", meta_style))
        story.append(Paragraph(f"<b>Version Reference:</b> {version_id}", meta_style))
        story.append(Paragraph("<b>Confidentiality:</b> Commercial In Confidence", meta_style))
        story.append(PageBreak())
        
        # Data extraction from compiled version
        data = version.output_data or {}
        
        biz = data.get("business_analysis", {})
        prd = data.get("product_requirements", {})
        stories = data.get("user_stories", [])
        arch = data.get("system_architecture", {})
        db_design = data.get("database_design", {})
        api = data.get("api_design", {})
        sec = data.get("security_review", {})
        
        # Section mapping builder helper
        def add_section(title, content_list):
            story.append(Paragraph(title, h1_style))
            # Divider line
            d = Table([[""]], colWidths=[504])
            d.setStyle(TableStyle([
                ('LINEBELOW', (0,0), (-1,-1), 1.5, PRIMARY_COLOR),
                ('BOTTOMPADDING', (0,0), (-1,-1), 0),
                ('TOPPADDING', (0,0), (-1,-1), 0)
            ]))
            story.append(d)
            story.append(Spacer(1, 10))
            
            for item in content_list:
                if isinstance(item, str):
                    story.append(Paragraph(item, body_style))
                else:
                    story.append(item)
            story.append(Spacer(1, 15))
        
        # 1. Executive Summary
        add_section("1. Executive Summary", [biz.get("executive_summary", "No executive summary available.")])
        
        # 2. Business Analysis
        add_section("2. Business Analysis", [
            Paragraph("Market Fit", h2_style),
            biz.get("market_fit", "No market fit details available."),
            Paragraph("Revenue Model", h2_style),
            biz.get("revenue_model", "No revenue model details available."),
            Paragraph("Competitor Analysis", h2_style),
            ", ".join(biz.get("competitor_analysis", [])) if biz.get("competitor_analysis") else "No competitors listed."
        ])
        
        # 3. User Personas
        personas = prd.get("user_personas", [])
        persona_elements = []
        for idx, p in enumerate(personas):
            persona_elements.append(Paragraph(f"Persona {idx+1}: {p.get('name', 'N/A')} ({p.get('role', 'N/A')})", h2_style))
            persona_elements.append(Paragraph(f"<b>Goals:</b> {p.get('goals', 'N/A')}", body_style))
            persona_elements.append(Paragraph(f"<b>Frustrations:</b> {p.get('frustrations', 'N/A')}", body_style))
        add_section("3. User Personas", persona_elements if persona_elements else ["No user personas generated."])
        
        # 4. Product Requirements
        add_section("4. Product Requirements", [prd.get("prd_details", "No product requirements specified.")])
        
        # 5. User Stories
        story_elements = []
        for idx, s in enumerate(stories):
            desc = f"<b>As a</b> {s.get('as_a', 'user')}, <b>I want to</b> {s.get('i_want_to', '')} <b>so that</b> {s.get('so_that', '')}"
            story_elements.append(Paragraph(f"<b>US-{idx+1}: {s.get('title', 'Story')}</b>", h2_style))
            story_elements.append(Paragraph(desc, body_style))
            if s.get("acceptance_criteria"):
                story_elements.append(Paragraph("<b>Acceptance Criteria:</b>", body_style))
                for ac in s.get("acceptance_criteria", []):
                    story_elements.append(Paragraph(f"- {ac}", body_style))
        add_section("5. User Stories", story_elements if story_elements else ["No user stories generated."])
        
        # 6. System Architecture
        add_section("6. System Architecture", [
            arch.get("overview", "No architecture overview available."),
            Spacer(1, 10),
            Paragraph("<b>Mermaid Diagram Definition:</b>", h2_style),
            Paragraph(f"<font face='Courier' size='8'>{arch.get('diagram', '')}</font>", body_style)
        ])
        
        # 7. Database Design
        add_section("7. Database Design", [
            db_design.get("overview", "No database overview available."),
            Spacer(1, 10),
            Paragraph("<b>PostgreSQL DDL:</b>", h2_style),
            Paragraph(f"<font face='Courier' size='7'>{db_design.get('schema_ddl', '')}</font>", body_style),
            Paragraph("<b>Indexing Strategy:</b>", h2_style),
            db_design.get("indexing_strategy", "No indexing details.")
        ])
        
        # 8. API Design
        api_elements = [Paragraph(api.get("overview", "No API overview details."), body_style)]
        endpoints = api.get("endpoints", [])
        for ep in endpoints:
            api_elements.append(Paragraph(f"<b>{ep.get('method', 'GET')} {ep.get('path', '/')}</b>", h2_style))
            api_elements.append(Paragraph(f"<i>Summary:</i> {ep.get('summary', '')}", body_style))
            api_elements.append(Paragraph(f"<i>Request Body:</i> {ep.get('request_body', 'None')}", body_style))
            api_elements.append(Paragraph(f"<i>Response Body:</i> {ep.get('response_body', 'None')}", body_style))
        api_elements.append(Paragraph("<b>Schema Definitions:</b>", h2_style))
        api_elements.append(Paragraph(api.get("schema_definitions", ""), body_style))
        add_section("8. API Design", api_elements)
        
        # 9. Security Analysis
        add_section("9. Security Analysis", [
            Paragraph("Security Strategy", h2_style),
            sec.get("strategy", "No security strategy details."),
            Paragraph("Authentication & Authorization", h2_style),
            sec.get("auth_review", "No auth strategy reviews."),
            Paragraph("OWASP Mitigation", h2_style),
            sec.get("owasp_mitigation", "No mitigation checklists.")
        ])
        
        # 10. Cost Estimation
        costs = data.get("cost_estimation", {})
        add_section("10. Cost Estimation", [
            Paragraph(f"<b>Infrastructure Cost:</b> {costs.get('infra_cost', 'N/A')}", body_style),
            Paragraph(f"<b>Development Cost:</b> {costs.get('development_cost', 'N/A')}", body_style),
            Paragraph(f"<b>Third-Party API Cost:</b> {costs.get('third_party_cost', 'N/A')}", body_style)
        ])
        
        # 11. Deployment Strategy
        deploy = data.get("deployment_plan", {})
        add_section("11. Deployment Strategy", [deploy.get("strategy", "No deployment strategy details.")])
        
        # 12. Scalability Plan
        scalability = data.get("scalability_planning", {})
        add_section("12. Scalability Plan", [scalability.get("plan", "No scalability plan details.")])
        
        # 13. Team Structure
        team = prd.get("team_structure", [])
        add_section("13. Team Structure", [", ".join(team) if team else "No roles specified."])
        
        # 14. Risk Assessment
        tech_docs = data.get("technical_documentation", {})
        risks = tech_docs.get("risks", [])
        risk_elements = []
        for r in risks:
            risk_elements.append(Paragraph(f"<b>Risk:</b> {r.get('risk', 'N/A')}", body_style))
            risk_elements.append(Paragraph(f"<b>Impact:</b> {r.get('impact', 'N/A')} | <b>Mitigation:</b> {r.get('mitigation', 'N/A')}", body_style))
        add_section("14. Risk Assessment", risk_elements if risk_elements else ["No risks logged."])
        
        # 15. AI Recommendations
        add_section("15. AI Recommendations", [
            "We recommend integrating logging systems (e.g. system_logs) and agent metrics early in deployment.",
            "Utilize localized vector indexing inside ChromaDB with chunk size 1000 for standard queries.",
            "Verify JWT token validation using PyJWT on every route."
        ])
        
        # 16. UI Blueprint
        add_section("16. UI Blueprint", [
            "Refer to Logo Studio and UI Generator dashboards for visual mockups and layout wireframes.",
            "Use TailwindCSS class tokens combined with custom fonts for a modern look."
        ])
        
        # 17. Implementation Roadmap
        roadmap = tech_docs.get("roadmap", [])
        roadmap_elements = []
        for step in roadmap:
            roadmap_elements.append(Paragraph(f"<b>Phase:</b> {step.get('phase', 'N/A')} - {step.get('milestone', 'N/A')}", h2_style))
            roadmap_elements.append(Paragraph(step.get('description', 'N/A'), body_style))
        add_section("17. Implementation Roadmap", roadmap_elements if roadmap_elements else ["No roadmap details generated."])

        # Build document
        doc.build(story, canvasmaker=NumberedCanvas)
        
        # Record report in database
        db_report = Report(
            project_version_id=uuid.UUID(version_id),
            pdf_path=pdf_path
        )
        db.add(db_report)
        db.commit()
        
        return pdf_path

pdf_builder = PDFReportBuilder()
