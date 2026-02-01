# How to Export Architecture Diagrams for Presentation

## Quick Export Methods

### Option 1: Screenshot from HTML File (Recommended ✅)

**File**: `ARCHITECTURE_DIAGRAMS_EXPORT.html`

1. Open the HTML file in your browser (should already be open)
2. Each diagram is on a white background, ready to capture
3. Take screenshots:
   - **Mac**: Press `Cmd + Shift + 4`, then drag to select the diagram area
   - **Windows**: Press `Win + Shift + S`, then drag to select the diagram area
4. Paste directly into your PowerPoint/Google Slides presentation

**Pro tip**: For best quality, make your browser window as large as possible before taking the screenshot.

---

### Option 2: Print to PDF

1. Open `ARCHITECTURE_DIAGRAMS_EXPORT.html` in your browser
2. Press `Ctrl/Cmd + P` to open print dialog
3. Select "Save as PDF" as the destination
4. Choose "Landscape" orientation for better diagram layout
5. Save the PDF
6. Extract individual pages as images using:
   - Preview (Mac): Open PDF → File → Export → Choose PNG format
   - Adobe Acrobat: Export PDF → Image → PNG
   - Online tools: pdf2png.com, ilovepdf.com

---

### Option 3: Online Mermaid Editor

**Website**: https://mermaid.live

1. Open the markdown file: `ARCHITECTURE_DIAGRAM.md`
2. Copy any Mermaid diagram code (the part between ` ```mermaid` and ` ``` `)
3. Go to https://mermaid.live
4. Paste the code in the editor
5. Click "PNG" or "SVG" to download high-quality images

**Benefits**:
- SVG format = perfect quality at any size (recommended for presentations)
- PNG format = good for quick screenshots
- Can adjust colors and styling before export

---

### Option 4: VS Code Extension (For Developers)

If you're using VS Code:

1. Install extension: "Markdown Preview Mermaid Support"
2. Open `ARCHITECTURE_DIAGRAM.md`
3. Press `Cmd/Ctrl + Shift + V` to preview
4. Right-click on any diagram → "Copy Image" or use screenshot tool

---

## Diagram Files Available

### Main Documentation
- **ARCHITECTURE_DIAGRAM.md** - Full technical documentation with all diagrams

### Export Files
- **ARCHITECTURE_DIAGRAMS_EXPORT.html** - Interactive HTML with all 5 diagrams
  - Diagram 1: High-Level System Architecture
  - Diagram 2: Detailed Component Architecture
  - Diagram 3: Client Need Matching Flow
  - Diagram 4: Employee Profile Building Flow
  - Diagram 5: Production Deployment Architecture

---

## Tips for PowerPoint/Slides

### Recommended Slide Layout

**Slide 1: System Overview**
- Use Diagram 1 (High-Level System Architecture)
- Title: "ASPIRE2026 System Architecture"
- Add bullet points:
  - Microservices-based architecture
  - React frontend with FastAPI backend
  - AI-powered by Azure OpenAI GPT-4o
  - Dual database for client and employee data

**Slide 2: Technical Components**
- Use Diagram 2 (Detailed Component Architecture)
- Title: "Component Architecture"
- Highlight: Layered architecture pattern

**Slide 3: AI Matching Process**
- Use Diagram 3 (Matching Flow)
- Title: "Intelligent Candidate Matching"
- Add bullet points:
  - AI-powered skill matching
  - Cross-database queries
  - Ranked recommendations with explanations

**Slide 4: Employee Onboarding**
- Use Diagram 4 (Profile Building Flow)
- Title: "Conversational Profile Building"
- Highlight: Real-time AI extraction

**Slide 5: Production Architecture** (Optional - for technical stakeholders)
- Use Diagram 5 (Deployment Architecture)
- Title: "Scalable Production Deployment"

---

## Image Quality Best Practices

1. **Resolution**: Aim for at least 1920x1080 (Full HD) screenshots
2. **Format**:
   - PNG for screenshots (lossless)
   - SVG for vector graphics (scalable)
   - Avoid JPG (lossy compression)
3. **Background**: All diagrams have white backgrounds for clean presentation
4. **Cropping**: Crop tightly around diagrams, leaving small margins

---

## Presentation Talking Points

### High-Level Architecture
- "ASPIRE2026 uses a microservices architecture with two independent services"
- "Frontend is built with modern React and TypeScript for fast, responsive UI"
- "Backend services communicate with Azure AI for intelligent processing"
- "Matching Agent can query both databases for comprehensive candidate search"

### Key Technical Highlights
- "AI-powered requirement extraction reduces manual data entry"
- "Real-time conversation processing builds profiles dynamically"
- "Transparent matching with detailed explanations for hiring decisions"
- "Speech-to-text and text-to-speech for accessible interfaces"

### Business Value
- "Reduces time-to-match from days to minutes"
- "AI provides explainable recommendations for compliance"
- "Conversational interface improves user experience"
- "Scalable architecture ready for growth"

---

## Need Different Formats?

If you need:
- **Higher resolution**: Use the mermaid.live SVG export
- **Different colors**: Edit the Mermaid code in the HTML file (search for `fill:#`)
- **Simplified diagrams**: Let me know which components to focus on
- **Custom diagrams**: Provide specific requirements

---

## Quick Command Reference

```bash
# Open HTML file in browser
open docs/ARCHITECTURE_DIAGRAMS_EXPORT.html

# Open in specific browser
open -a "Google Chrome" docs/ARCHITECTURE_DIAGRAMS_EXPORT.html
open -a "Safari" docs/ARCHITECTURE_DIAGRAMS_EXPORT.html

# View markdown in VS Code
code docs/ARCHITECTURE_DIAGRAM.md
```

---

## Troubleshooting

**Diagrams not rendering in HTML?**
- Make sure you have internet connection (loads Mermaid from CDN)
- Try a different browser (Chrome/Firefox recommended)
- Clear browser cache

**Diagrams look blurry in presentation?**
- Take larger screenshots (maximize browser window)
- Use SVG export from mermaid.live instead
- Increase image resolution in PowerPoint (Format → Compress Pictures → Use original resolution)

**Need to edit diagrams?**
- Edit the ARCHITECTURE_DIAGRAMS_EXPORT.html file
- Find the `<div class="mermaid">` sections
- Modify the Mermaid code
- Refresh browser to see changes

---

**Last Updated**: February 1, 2026
