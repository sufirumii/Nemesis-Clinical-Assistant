"""
Gradio UI for LlamaTron RS1 Nemesis Clinical Decision Support Agent.
Large, readable, professional medical interface.
"""
import os, uuid, httpx, gradio as gr
from backend.core.config import get_settings

cfg = get_settings()
API_BASE = f"http://127.0.0.1:{cfg.api_port}"

# ── helpers ──────────────────────────────────────────────────────────────────

def analyze(symptoms: str, age: str, sex: str, session_id: str, history: list):
    if not symptoms.strip():
        return history, session_id, "", "", "", ""

    if not session_id:
        session_id = str(uuid.uuid4())[:8]

    payload = {
        "session_id": session_id,
        "symptoms": symptoms,
        "patient_age": int(age) if age.isdigit() else None,
        "patient_sex": sex.lower() if sex else None,
    }

    try:
        r = httpx.post(f"{API_BASE}/analyze", json=payload, timeout=120)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        error_msg = f"⚠️ API error: {e}"
        history.append({"role": "user", "content": symptoms})
        history.append({"role": "assistant", "content": error_msg})
        return history, session_id, "", "", "", ""

    history.append({"role": "user", "content": symptoms})
    history.append({"role": "assistant", "content": data["full_response"]})

    return (
        history,
        session_id,
        data.get("reasoning", ""),
        data.get("differentials", ""),
        data.get("treatment", ""),
        data.get("red_flags", ""),
    )


def export_pdf(session_id: str, age: str, sex: str):
    if not session_id:
        return None
    payload = {
        "session_id": session_id,
        "patient_age": int(age) if age.isdigit() else None,
        "patient_sex": sex.lower() if sex else None,
    }
    try:
        r = httpx.post(f"{API_BASE}/export-pdf", json=payload, timeout=60)
        r.raise_for_status()
    except Exception as e:
        gr.Warning(f"PDF export failed: {e}")
        return None

    path = f"/tmp/nemesis_{session_id}.pdf"
    with open(path, "wb") as f:
        f.write(r.content)
    return path


def clear_session(session_id: str):
    if session_id:
        try:
            httpx.delete(f"{API_BASE}/history/{session_id}", timeout=10)
        except Exception:
            pass
    return [], str(uuid.uuid4())[:8], "", "", "", ""


# ── CSS ───────────────────────────────────────────────────────────────────────
CSS = """
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
  --teal-900: #0F3D38;
  --teal-700: #0D6B62;
  --teal-500: #0D9488;
  --teal-300: #5EEAD4;
  --teal-100: #CCFBF1;
  --teal-50:  #F0FDFA;
  --slate-900: #0F172A;
  --slate-700: #334155;
  --slate-400: #94A3B8;
  --slate-100: #F1F5F9;
  --red: #DC2626;
  --font-display: 'DM Serif Display', Georgia, serif;
  --font-body: 'DM Sans', system-ui, sans-serif;
}

body, .gradio-container {
  font-family: var(--font-body) !important;
  background: var(--teal-50) !important;
}

/* ─── Hero header ─── */
#hero {
  background: linear-gradient(135deg, var(--teal-900) 0%, var(--teal-700) 60%, var(--teal-500) 100%);
  border-radius: 20px;
  padding: 40px 48px 36px;
  margin-bottom: 24px;
  position: relative;
  overflow: hidden;
}
#hero::after {
  content: '';
  position: absolute;
  right: -60px; top: -60px;
  width: 280px; height: 280px;
  border-radius: 50%;
  background: rgba(255,255,255,0.04);
  pointer-events: none;
}
#hero-title {
  font-family: var(--font-display) !important;
  font-size: 2.8rem !important;
  color: #ffffff !important;
  margin: 0 !important;
  line-height: 1.15 !important;
  letter-spacing: -0.5px;
}
#hero-sub {
  font-size: 1.1rem !important;
  color: var(--teal-300) !important;
  margin-top: 8px !important;
}
#hero-badge {
  display: inline-block;
  background: rgba(255,255,255,0.12);
  border: 1px solid rgba(255,255,255,0.2);
  color: #fff;
  border-radius: 100px;
  padding: 4px 14px;
  font-size: 0.78rem;
  margin-top: 14px;
  letter-spacing: 0.5px;
  font-weight: 500;
}

/* ─── Input card ─── */
#input-card {
  background: #fff;
  border-radius: 16px;
  padding: 28px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.07), 0 4px 20px rgba(13,148,136,0.08);
  border: 1px solid var(--teal-100);
}

/* ─── Labels ─── */
label span {
  font-size: 0.92rem !important;
  font-weight: 600 !important;
  color: var(--slate-700) !important;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

/* ─── Symptom textarea ─── */
#symptoms-input textarea {
  font-size: 1.05rem !important;
  line-height: 1.7 !important;
  border-radius: 12px !important;
  border: 2px solid var(--teal-100) !important;
  padding: 14px 16px !important;
  min-height: 120px !important;
  transition: border 0.2s;
}
#symptoms-input textarea:focus {
  border-color: var(--teal-500) !important;
  outline: none !important;
  box-shadow: 0 0 0 3px rgba(13,148,136,0.1) !important;
}

/* ─── Buttons ─── */
#btn-analyze {
  background: linear-gradient(135deg, var(--teal-700), var(--teal-500)) !important;
  color: #fff !important;
  font-size: 1.05rem !important;
  font-weight: 600 !important;
  border-radius: 12px !important;
  padding: 14px 28px !important;
  border: none !important;
  cursor: pointer;
  transition: transform 0.15s, box-shadow 0.15s;
}
#btn-analyze:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(13,148,136,0.35) !important;
}
#btn-clear {
  background: var(--slate-100) !important;
  color: var(--slate-700) !important;
  font-size: 0.95rem !important;
  border-radius: 12px !important;
  border: 1px solid #e2e8f0 !important;
  padding: 13px 20px !important;
}
#btn-pdf {
  background: #fff !important;
  color: var(--teal-700) !important;
  font-size: 0.95rem !important;
  border-radius: 12px !important;
  border: 2px solid var(--teal-500) !important;
  padding: 12px 20px !important;
  font-weight: 600 !important;
}

/* ─── Chat ─── */
#chatbox .message {
  font-size: 1rem !important;
  line-height: 1.7 !important;
  border-radius: 14px !important;
  padding: 16px 20px !important;
  max-width: 92% !important;
}
#chatbox .message.user {
  background: var(--teal-100) !important;
  color: var(--teal-900) !important;
  margin-left: auto;
  font-weight: 500;
}
#chatbox .message.bot {
  background: #fff !important;
  border: 1px solid var(--teal-100) !important;
  color: var(--slate-900) !important;
}

/* ─── Analysis panels ─── */
.analysis-panel {
  background: #fff;
  border-radius: 14px;
  border: 1px solid var(--teal-100);
  padding: 20px 22px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}
.analysis-panel textarea {
  font-size: 0.97rem !important;
  line-height: 1.65 !important;
  color: var(--slate-900) !important;
  border: none !important;
  background: transparent !important;
  resize: vertical;
}
#red-flags-panel {
  border-left: 4px solid var(--red) !important;
}
#red-flags-panel textarea {
  color: var(--red) !important;
  font-weight: 500 !important;
}

/* ─── Section titles ─── */
.section-title {
  font-family: var(--font-display) !important;
  font-size: 1.25rem !important;
  color: var(--teal-700) !important;
  margin-bottom: 16px !important;
  padding-bottom: 8px !important;
  border-bottom: 2px solid var(--teal-100);
}

/* ─── Disclaimer ─── */
#disclaimer {
  text-align: center;
  font-size: 0.8rem;
  color: var(--slate-400);
  margin-top: 24px;
  padding: 16px;
  border-top: 1px solid var(--teal-100);
}
"""

# ── UI ────────────────────────────────────────────────────────────────────────
with gr.Blocks(css=CSS, title="LlamaTron RS1 Nemesis — CDS Agent") as demo:

    session_id_state = gr.State(str(uuid.uuid4())[:8])

    # Hero
    gr.HTML("""
    <div id="hero">
      <div id="hero-title">LlamaTron RS1 Nemesis</div>
      <div id="hero-sub">Clinical Decision Support Agent</div>
      <div id="hero-badge">🧠 Powered by Llama-3.2-1B · Fine-tuned on 204K Clinical Conversations</div>
    </div>
    """)

    with gr.Row(equal_height=False):

        # ── Left column: inputs ───────────────────────────────────────────
        with gr.Column(scale=4):
            with gr.Group(elem_id="input-card"):
                gr.Markdown("### 🩺 Patient Information", elem_classes="section-title")

                symptoms_input = gr.Textbox(
                    label="Symptoms & Clinical Presentation",
                    placeholder=(
                        "Describe symptoms in detail…\n"
                        "e.g. 45-year-old female, 3-day history of high fever (39.5°C), "
                        "productive cough with greenish sputum, right-sided pleuritic chest pain, "
                        "mild dyspnoea on exertion. Non-smoker, no known allergies."
                    ),
                    lines=6,
                    elem_id="symptoms-input",
                )

                with gr.Row():
                    age_input = gr.Textbox(label="Age", placeholder="e.g. 45", scale=1)
                    sex_input = gr.Dropdown(
                        label="Sex", choices=["", "male", "female", "other"],
                        value="", scale=1,
                    )
                    session_display = gr.Textbox(
                        label="Session ID", interactive=False,
                        value=str(uuid.uuid4())[:8], scale=2,
                    )

                with gr.Row():
                    btn_analyze = gr.Button("🔬 Analyze", elem_id="btn-analyze", scale=3)
                    btn_clear = gr.Button("🗑 New Session", elem_id="btn-clear", scale=1)
                    btn_pdf = gr.Button("📄 Export PDF", elem_id="btn-pdf", scale=1)

        # ── Right column: chat ────────────────────────────────────────────
        with gr.Column(scale=6):
            gr.Markdown("### 💬 Clinical Dialogue", elem_classes="section-title")
            chatbox = gr.Chatbot(
                label="",
                height=440,
                type="messages",
                elem_id="chatbox",
                avatar_images=(None, "🧠"),
                show_label=False,
                bubble_full_width=False,
            )

    # ── Analysis detail panels ────────────────────────────────────────────────
    gr.Markdown("---")
    gr.Markdown("### 🔍 Detailed Analysis Breakdown", elem_classes="section-title")

    with gr.Row():
        reasoning_box = gr.Textbox(
            label="🧠 Chain-of-Thought Reasoning",
            lines=8, interactive=False,
            elem_classes="analysis-panel",
        )
        differentials_box = gr.Textbox(
            label="📋 Differential Diagnoses",
            lines=8, interactive=False,
            elem_classes="analysis-panel",
        )

    with gr.Row():
        treatment_box = gr.Textbox(
            label="💊 Treatment Plan",
            lines=6, interactive=False,
            elem_classes="analysis-panel",
        )
        red_flags_box = gr.Textbox(
            label="⚠️ Red Flags / Escalation",
            lines=6, interactive=False,
            elem_classes="analysis-panel",
            elem_id="red-flags-panel",
        )

    pdf_file = gr.File(label="📥 Download Report", visible=True)

    gr.HTML("""
    <div id="disclaimer">
      ⚠️ <strong>DISCLAIMER:</strong> LlamaTron RS1 Nemesis is intended for research and
      educational purposes only. It is <strong>not</strong> a substitute for professional
      medical advice, diagnosis, or treatment. Always consult a qualified healthcare provider.
    </div>
    """)

    # ── Wiring ────────────────────────────────────────────────────────────────
    btn_analyze.click(
        fn=analyze,
        inputs=[symptoms_input, age_input, sex_input, session_id_state, chatbox],
        outputs=[chatbox, session_id_state, reasoning_box, differentials_box,
                 treatment_box, red_flags_box],
    ).then(
        fn=lambda sid: sid,
        inputs=[session_id_state],
        outputs=[session_display],
    )

    symptoms_input.submit(
        fn=analyze,
        inputs=[symptoms_input, age_input, sex_input, session_id_state, chatbox],
        outputs=[chatbox, session_id_state, reasoning_box, differentials_box,
                 treatment_box, red_flags_box],
    )

    btn_clear.click(
        fn=clear_session,
        inputs=[session_id_state],
        outputs=[chatbox, session_id_state, reasoning_box, differentials_box,
                 treatment_box, red_flags_box],
    ).then(
        fn=lambda sid: sid,
        inputs=[session_id_state],
        outputs=[session_display],
    )

    btn_pdf.click(
        fn=export_pdf,
        inputs=[session_id_state, age_input, sex_input],
        outputs=[pdf_file],
    )


if __name__ == "__main__":
    demo.launch(
        server_port=cfg.gradio_port,
        share=cfg.gradio_share,
        show_api=False,
    )
