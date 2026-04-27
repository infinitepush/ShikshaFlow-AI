# 🎓 ShikshaFLow
### AI-Powered Platform to Instantly Create and Animate Educational Materials


---

## 🧠 Overview  

*EduBuilder AI* revolutionizes how educators, trainers, and content creators design lessons.  
Just type a topic — and within minutes, receive *slides, video, voiceover, quizzes, and interactive animations* ready to teach or present.  

> “From text to teaching assets — in minutes, not hours.”

---

## 🚀 Core Modules  

### 🏠 *Home*  
A personalized dashboard showcasing:
- Recent lectures, downloads, and quiz stats  
- Quick-access shortcuts to generate new lessons  
- Progress tracking for active sessions  

---

### 🧩 *Generate Lecture*  
Transform a simple text prompt into complete educational material.  
*Input Example:*  
> “Explain the water cycle for 7th-grade students in a 4-minute lecture.”

*Generates:*
- 🖼 Slide Deck (PDF/Google Slides export)  
- 🎙 AI Script + Voiceover (MP3)  
- 🎞 Auto-synced Video (MP4)  
- 🧾 Quiz (3 auto-generated MCQs)

You can also:
- Pick a *Visual Theme*: Minimalist / Chalkboard / Corporate  
- Customize font, color, and background  
- Download or share instantly  

---

### 🎬 *Animation Studio*  
Bring your lectures to life with *step-by-step interactive animations.*  
Add dynamic explanations like:
- 🌿 “Photosynthesis Process”  
- ❤ “How the Heart Pumps Blood”  
- 💻 “Bubble Sort Algorithm”

*Features:*
- Framer Motion-based animated sequences  
- User-controlled steps (“Next → Step 2 → Step 3”)  
- Real-time narration sync  
- Interactive micro-quizzes  

---

### 🧠 *My Quizzes*  
Automatically generated multiple-choice questions for every lecture.  
- 3 smart MCQs per topic  
- Editable and exportable format for LMS  
- Performance tracking for learners  

---

### 📥 *Downloads*  
Centralized library for all generated content:
- 🎞 Videos (.MP4)  
- 🖼 Slides (.PDF)  
- 🎧 Voiceovers (.MP3)  
- 🧾 Quiz Sets (.TXT / .CSV)

Filter and re-download anytime.  

---

### 💬 *Doubt Sessions*  
AI-powered Q&A environment where learners can:
- Ask topic-specific questions  
- Get instant, AI-curated explanations  
- Schedule group or 1-on-1 sessions  
- Integrate with live chat (Gemini API or Socket-based interaction)

---

### 👤 *Profile*  
Personalized space for users:
- Manage generated content history  
- Update visual and voice preferences  
- Track learning insights and achievements  

---

### 🔓 *Logout*  
Secure logout and session handling.  
(Integrated JWT / OAuth authentication coming soon.)

---

## 🌟 Bonus Features  

| Category | Feature | Description |
|-----------|----------|-------------|
| 🧠 Learning | Smart Quiz Generator | Auto-generates MCQs from lecture content |
| 🎨 Customization | Visual Theme Selector | Choose Minimalist, Chalkboard, or Corporate themes |
| 🗣 Accessibility | Voiceover in multiple accents | Male/Female voice options |
| ⚡ Efficiency | 1-Click Downloads | Slides, video, and audio generated instantly |
| 📚 Pedagogy | CO & Bloom’s Mapping (planned) | Tag content outcomes and learning levels |

---

## 🔮 Future Vision: Interactive Learning 2.0  

> “Transform passive viewing into immersive learning.”

Phase Two introduces:
- Step-by-step *interactive animations*
- *Learner-driven controls* (reveal, click, respond)
- Real-time *feedback loops*
- Built-in *AI explainer avatars*

---

## 🧰 Tech Stack  

| Layer | Technology |
|-------|-------------|
| 💻 Frontend | React + TypeScript + Tailwind + Framer Motion |
| 🧠 AI Core | Gemini API (Text generation for lectures, plans, quizzes, and chat) |
| 🧩 Backend | Flask (Python) |
| 🗂 Media Engine | MoviePy + gTTS + FFmpeg |
| ☁ Deployment | Render / Vercel |
| 📦 Storage | S3-compatible bucket / Local FS |

---

## 🧪 Example Input & Output  

*Prompt:*  
> “Explain Newton’s Laws of Motion for high school students in a 5-minute video.”

*Output:*
- 📑 Slides: 6 slides with headings & visuals  
- 🗣 Voiceover: Natural narration synced with slides  
- 🎞 Video: Auto-generated 720p MP4  
- 🧾 Quiz: 3 conceptual MCQs  

---

## 🏁 Getting Started  

### 1️⃣ Clone the Repository  
```bash
git clone https://github.com/yourusername/edubuilder-ai.git
cd edubuilder-ai

