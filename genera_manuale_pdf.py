# -*- coding: utf-8 -*-
import os
import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas
from PIL import Image as PILImage

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super().showPage()
        super().save()

    def draw_header_footer(self, page_count):
        if self._pageNumber == 1:
            return  # Nessuna intestazione/piè di pagina sulla copertina

        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#64748B"))

        # Header
        self.drawString(20 * mm, 285 * mm, "CAMPIONATO SERIE A 2026/27 — MANUALE UTENTE & GUIDA TECNICA")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(20 * mm, 282 * mm, 190 * mm, 282 * mm)

        # Footer
        page_text = f"Pagina {self._pageNumber} di {page_count}"
        self.setFont("Helvetica", 9)
        self.drawRightString(190 * mm, 12 * mm, page_text)
        self.drawString(20 * mm, 12 * mm, "Progetto Campionato di Pierfrancesco — Riservato & Confidenziale")
        self.line(20 * mm, 16 * mm, 190 * mm, 16 * mm)
        self.restoreState()


def crea_manuale_pdf(output_pdf="Manuale_Utente_Campionato_SerieA.pdf"):
    doc = SimpleDocTemplate(
        output_pdf,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=22 * mm,
        bottomMargin=22 * mm
    )

    styles = getSampleStyleSheet()
    
    # Palette colori
    c_primary = colors.HexColor("#0F172A")    # Deep Slate
    c_navy = colors.HexColor("#1E3A8A")       # Navy Blue
    c_accent = colors.HexColor("#D97706")     # Gold Accent
    c_subtext = colors.HexColor("#475569")    # Text Dark
    c_bg_box = colors.HexColor("#F8FAFC")     # Soft Box Background
    c_border_box = colors.HexColor("#E2E8F0")

    # Stili tipografici personalizzati
    style_cover_title = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=28,
        leading=34,
        textColor=c_navy,
        alignment=1, # Center
        spaceAfter=15
    )
    style_cover_sub = ParagraphStyle(
        'CoverSub',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=20,
        textColor=c_accent,
        alignment=1,
        spaceAfter=25
    )
    style_cover_meta = ParagraphStyle(
        'CoverMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=16,
        textColor=c_subtext,
        alignment=1
    )
    style_h1 = ParagraphStyle(
        'H1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=c_navy,
        spaceBefore=16,
        spaceAfter=10,
        keepWithNext=True
    )
    style_h2 = ParagraphStyle(
        'H2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=c_accent,
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )
    style_body = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14.5,
        textColor=c_subtext,
        spaceAfter=8
    )
    style_body_bold = ParagraphStyle(
        'BodyBold',
        parent=style_body,
        fontName='Helvetica-Bold'
    )
    style_bullet = ParagraphStyle(
        'Bullet',
        parent=style_body,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )
    style_callout = ParagraphStyle(
        'Callout',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#1E293B"),
    )
    style_table_header = ParagraphStyle(
        'TH',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        textColor=colors.white,
        alignment=1
    )
    style_table_cell = ParagraphStyle(
        'TC',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=c_subtext
    )

    story = []

    def make_callout(text, bg_color="#EFF6FF", border_color="#3B82F6", title="NOTA"):
        content = [
            Paragraph(f"<b>{title}:</b> {text}", style_callout)
        ]
        t = Table([[content]], colWidths=[174 * mm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor(bg_color)),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor(border_color)),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))
        return t

    def add_image_safe(path, max_width=174*mm, max_height=100*mm, caption=""):
        if os.path.exists(path):
            try:
                with PILImage.open(path) as img:
                    orig_w, orig_h = img.size
                ratio = min(max_width / orig_w, max_height / orig_h)
                w = orig_w * ratio
                h = orig_h * ratio
                img_flow = RLImage(path, width=w, height=h)
                story.append(Spacer(1, 4 * mm))
                story.append(img_flow)
                if caption:
                    story.append(Spacer(1, 2 * mm))
                    story.append(Paragraph(f"<i>Figura — {caption}</i>", ParagraphStyle('Cap', parent=style_body, fontSize=8, alignment=1, textColor=colors.HexColor("#64748B"))))
                story.append(Spacer(1, 4 * mm))
            except Exception as e:
                story.append(Paragraph(f"[Immagine {path} non disponibile: {e}]", style_body))

    # =========================================================================
    # COPERTINA
    # =========================================================================
    story.append(Spacer(1, 25 * mm))
    story.append(Paragraph("⚽ CAMPIONATO SERIE A 2026/2027", style_cover_sub))
    story.append(Paragraph("MANUALE UTENTE & GUIDA TECNICA", style_cover_title))
    story.append(HRFlowable(width="80%", thickness=2, color=c_accent, spaceAfter=20, spaceBefore=10))
    story.append(Paragraph("Suite Desktop ad Alte Prestazioni per l'Analisi Statistica, la Classifica Ufficiale e la Predizione Algoritmica delle Partite di Serie A", ParagraphStyle('CoverDesc', parent=style_body, fontSize=12, leading=17, alignment=1, textColor=c_primary)))
    
    story.append(Spacer(1, 15 * mm))
    # Immagine di copertina
    if os.path.exists("manuale_assets/01_frontespizio.png"):
        add_image_safe("manuale_assets/01_frontespizio.png", max_width=170*mm, max_height=80*mm, caption="Schermata Principale dell'Applicazione con Banner Gioco Responsabile")

    story.append(Spacer(1, 15 * mm))
    meta_box = [
        [Paragraph("<b>Autore:</b> Pierfrancesco", style_cover_meta)],
        [Paragraph("<b>Versione:</b> 2.5 (High Performance Edition)", style_cover_meta)],
        [Paragraph("<b>Data Rilascio:</b> Settembre 2026", style_cover_meta)],
        [Paragraph("<b>Tecnologie:</b> Python 3.13 | PyQt5 | Pandas | Matplotlib | Machine Learning Heuristics", style_cover_meta)]
    ]
    t_meta = Table(meta_box, colWidths=[174 * mm])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F1F5F9")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    story.append(t_meta)
    story.append(PageBreak())

    # =========================================================================
    # INDICE DEI CONTENUTI
    # =========================================================================
    story.append(Paragraph("📑 Indice Generale del Manuale", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=c_navy, spaceAfter=15, spaceBefore=5))

    toc_data = [
        [Paragraph("<b>1. Panoramica del Progetto & Architettura</b>", style_body), Paragraph("Pagina 3", style_body)],
        [Paragraph("<b>2. Schermata Principale (Frontespizio)</b>", style_body), Paragraph("Pagina 4", style_body)],
        [Paragraph("<b>3. Modulo Classifica & Dati Sky Sport</b>", style_body), Paragraph("Pagina 5", style_body)],
        [Paragraph("<b>4. Modulo Statistiche & Trend Squadre</b>", style_body), Paragraph("Pagina 6", style_body)],
        [Paragraph("<b>5. Modulo Predizioni Partite & Intelligenza Algoritmica</b>", style_body), Paragraph("Pagina 7", style_body)],
        [Paragraph("<b>6. Modulo Aggiornamento Risultati (Web Scraping Live)</b>", style_body), Paragraph("Pagina 8", style_body)],
        [Paragraph("<b>7. Gestione Dati, Performance e Risoluzione Problemi</b>", style_body), Paragraph("Pagina 9", style_body)],
    ]
    t_toc = Table(toc_data, colWidths=[145 * mm, 29 * mm])
    t_toc.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
    ]))
    story.append(t_toc)
    story.append(Spacer(1, 10 * mm))

    # =========================================================================
    # CAPITOLO 1: PANORAMICA DEL PROGETTO
    # =========================================================================
    story.append(Paragraph("1. Panoramica del Progetto & Architettura", style_h1))
    story.append(Paragraph(
        "L'applicazione <b>Campionato Serie A 2026/27</b> è un sistema software desktop avanzato sviluppato in Python e PyQt5, "
        "concepito per offrire un'analisi statistica approfondita, la consultazione della classifica ufficiale e la generazione "
        "di predizioni probabilistiche basate su storici pluriennali e rendimenti in tempo reale.",
        style_body
    ))
    story.append(Paragraph(
        "<b>Pilastri dell'Architettura ad Alte Prestazioni:</b>", style_body_bold
    ))
    story.append(Paragraph("• <b>Warmup Silenzioso in Background:</b> All'avvio dell'applicazione, un thread parallelo a bassa priorità pre-riscalda in memoria i moduli più pesanti (Pandas, Matplotlib, Numpy) e pre-carica i dataset CSV.", style_bullet))
    story.append(Paragraph("• <b>Cache RAM Nativa dei DataFrame:</b> Le letture ripetute da disco sono state eliminate. Le strutture dati vengono caricate una sola volta in memoria RAM con invalidazione automatica quando viene eseguito un aggiornamento.", style_bullet))
    story.append(Paragraph("• <b>Rendering Istantaneo (&lt; 250 ms):</b> Le viste tabellari e i dialoghi secondari (Classifica, Statistiche, Predizioni) memorizzano le istanze attive per un'apertura istantanea alle riaperture successive.", style_bullet))
    story.append(Paragraph("• <b>Persistenza 100% CSV:</b> Totale eliminazione delle dipendenze da file Excel legacy a favore di file CSV ottimizzati e leggeri.", style_bullet))

    story.append(Spacer(1, 4 * mm))
    story.append(make_callout(
        "Il tempo di avvio alla prima videata è stato ottimizzato da circa 53 secondi a meno di 4 secondi, garantendo una fluidità d'uso professionale.",
        bg_color="#FEF3C7", border_color="#F59E0B", title="PERFORMANCE MILESTONE"
    ))
    story.append(PageBreak())

    # =========================================================================
    # CAPITOLO 2: FRONTESPIZIO & SCHERMATA PRINCIPALE
    # =========================================================================
    story.append(Paragraph("2. Schermata Principale (Frontespizio)", style_h1))
    story.append(Paragraph(
        "La schermata iniziale accoglie l'utente con una grafica moderna e accattivante a risoluzione Full HD (1920x1000), "
        "strutturata in tre aree operative chiave:",
        style_body
    ))
    
    story.append(Paragraph("<b>Componenti della Schermata:</b>", style_body_bold))
    story.append(Paragraph("1. <b>Barra Superiore degli Scudetti (20 Squadre):</b> Contiene i pulsanti con i loghi ufficiali di tutte le 20 squadre della Serie A 2026/27. Cliccando su ciascun logo si apre istantaneamente nel browser web predefinito il sito internet ufficiale della squadra.", style_bullet))
    story.append(Paragraph("2. <b>Banner Gioco Responsabile:</b> Posizionato al centro dello schermo subito sotto la fascia degli scudetti, presenta in stile glassmorphism con bordo dorato la frase d'effetto: <i>« Giocare è bello, farlo in modo responsabile è meglio! »</i>.", style_bullet))
    story.append(Paragraph("3. <b>Pannello di Navigazione Rapida (In basso a destra):</b> Raggruppa i comandi per accedere ai vari moduli:", style_bullet))
    story.append(Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;• <b>Aggiorna Risultati:</b> Avvia il web scraper live per scaricare le ultime partite giocate da internet.", style_bullet))
    story.append(Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;• <b>Classifica & Info:</b> Apre la tabella della classifica completa e i servizi Sky Sport.", style_bullet))
    story.append(Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;• <b>Statistiche & Grafici:</b> Apre il cruscotto di analisi del rendimento e dei trend.", style_bullet))
    story.append(Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;• <b>Predizioni:</b> Apre il simulatore di calcolo probabilità e scommesse AI.", style_bullet))
    story.append(Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;• <b>Esci da Campionato:</b> Chiude in modo sicuro l'applicazione e tutti i processi attivi.", style_bullet))

    add_image_safe("manuale_assets/01_frontespizio.png", max_width=174*mm, max_height=85*mm, caption="Frontespizio con barra scudetti, banner centrale e menu di navigazione")
    story.append(PageBreak())

    # =========================================================================
    # CAPITOLO 3: MODULO CLASSIFICA & SKY SPORT
    # =========================================================================
    story.append(Paragraph("3. Modulo Classifica & Informazioni Serie A", style_h1))
    story.append(Paragraph(
        "Il modulo Classifica (accessibile tramite il pulsante <i>Classifica & Info</i>) visualizza la graduatoria aggiornata "
        "del campionato di Serie A rispettando l'ordine standard dei dati ufficiali.",
        style_body
    ))

    story.append(Paragraph("<b>Struttura delle Colonne:</b>", style_body_bold))
    story.append(Paragraph("<code>Pos | Squadra | Punti | PG | V | P | S | GF | GS | DR</code>", ParagraphStyle('Code', parent=style_body, fontName='Courier-Bold', fontSize=9, textColor=c_navy)))
    story.append(Spacer(1, 2 * mm))

    story.append(Paragraph("<b>Codifica Cromatica delle Posizioni UEFA & Retrocessione:</b>", style_body_bold))
    
    color_table_data = [
        [Paragraph("<b>Posizione</b>", style_table_header), Paragraph("<b>Zona Competizione</b>", style_table_header), Paragraph("<b>Colore Sfondo</b>", style_table_header), Paragraph("<b>Colore Testo</b>", style_table_header)],
        [Paragraph("1ª — 4ª", style_table_cell), Paragraph("Champions League", style_table_cell), Paragraph("🟦 Blu (#007BFF)", style_table_cell), Paragraph("Bianco", style_table_cell)],
        [Paragraph("5ª — 6ª", style_table_cell), Paragraph("Europa League", style_table_cell), Paragraph("🟨 Giallo (#FFD700)", style_table_cell), Paragraph("Scuro (#212529)", style_table_cell)],
        [Paragraph("7ª", style_table_cell), Paragraph("Conference League", style_table_cell), Paragraph("🟩 Verde (#28A745)", style_table_cell), Paragraph("Bianco", style_table_cell)],
        [Paragraph("8ª — 17ª", style_table_cell), Paragraph("Zona Neutra (Salvezza)", style_table_cell), Paragraph("⬜ Bianco (#FFFFFF)", style_table_cell), Paragraph("Scuro (#212529)", style_table_cell)],
        [Paragraph("18ª — 20ª", style_table_cell), Paragraph("Zona Retrocessione", style_table_cell), Paragraph("🟥 Rosso (#DC3545)", style_table_cell), Paragraph("Bianco", style_table_cell)],
    ]
    t_colors = Table(color_table_data, colWidths=[25 * mm, 55 * mm, 50 * mm, 44 * mm])
    t_colors.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_navy),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
    ]))
    story.append(t_colors)
    story.append(Spacer(1, 4 * mm))

    story.append(Paragraph("<b>Integrazione Servizi Live Sky Sport:</b>", style_body_bold))
    story.append(Paragraph("Sulla destra della tabella sono presenti pulsanti ad accesso rapido per consultare in tempo reale su Sky Sport: "
                           "<b>🏆 Classifica Ufficiale</b>, <b>📊 Risultati e Calendario</b>, <b>⚽ Ultime News</b>, <b>📋 Probabili Formazioni</b> e <b>🎥 Video Highlights</b>.", style_body))

    add_image_safe("manuale_assets/02_classifica.png", max_width=174*mm, max_height=75*mm, caption="Schermata Classifica Serie A con colorazione UEFA e pulsanti Sky Sport")
    story.append(PageBreak())

    # =========================================================================
    # CAPITOLO 4: MODULO STATISTICHE & GRAFICI
    # =========================================================================
    story.append(Paragraph("4. Modulo Statistiche & Trend Squadre", style_h1))
    story.append(Paragraph(
        "Il modulo Statistiche analizza le performance aggregate di ogni singola squadra, scomponendo i dati per fornire "
        "un quadro dettagliato sull'affidabilità e sullo stato di forma:",
        style_body
    ))
    story.append(Paragraph("• <b>Rendimento Casa vs Trasferta:</b> Confronto immediato tra i punti conquistati tra le mura amiche e quelli ottenuti fuori casa.", style_bullet))
    story.append(Paragraph("• <b>Efficienza Offensiva e Difensiva:</b> Media goal fatti e subiti, calcolo della differenza reti ponderata e clean sheet.", style_bullet))
    story.append(Paragraph("• <b>Forma Recente (Ultime 5 Giornate):</b> Calcolo del punteggio forma su base 15 punti disponibili per individuare trend positivi o crisi di risultati.", style_bullet))
    story.append(Paragraph("• <b>Grafici Dinamici Matplotlib:</b> Generazione automatica di grafici ad alta risoluzione visualizzabili direttamente a schermo o salvabili in locale.", style_bullet))

    add_image_safe("manuale_assets/03_statistiche.png", max_width=174*mm, max_height=90*mm, caption="Cruscotto Statistiche e visualizzazione dei trend della Serie A")
    story.append(PageBreak())

    # =========================================================================
    # CAPITOLO 5: MODULO PREDIZIONI AI
    # =========================================================================
    story.append(Paragraph("5. Modulo Predizioni Partite & Intelligenza Algoritmica", style_h1))
    story.append(Paragraph(
        "Il modulo Predizioni costituisce il cuore analitico avanzato dell'applicazione. Selezionando la <b>Squadra Casa</b> e la <b>Squadra Trasferta</b>, "
        "il sistema esegue un'elaborazione multivariata istantanea sintetizzando centinaia di parametri storici e attuali.",
        style_body
    ))

    story.append(Paragraph("<b>Come Funziona il Motore di Calcolo:</b>", style_body_bold))
    story.append(Paragraph("1. <b>Fattore Campo & Ranking Attuale:</b> Ponderazione del ranking della squadra in casa vs il ranking in trasferta della sfidante.", style_bullet))
    story.append(Paragraph("2. <b>Forma Recente (Rolling 5 Matches):</b> Analisi delle ultime 5 partite con peso decrescente nel tempo.", style_bullet))
    story.append(Paragraph("3. <b>Archivio Storico Pluriennale:</b> Confronto con oltre 260 partite storiche memorizzate in <code>CampionatiPrecedenti.csv</code> per identificare le 'bestie nere' e i trend di lungo periodo.", style_bullet))
    story.append(Paragraph("4. <b>Stima Goal Previsti & Probabilità Esito:</b> Calcolo della distribuzione attesa dei goal totali e assegnazione delle probabilità su 1, X e 2.", style_bullet))

    story.append(Spacer(1, 3 * mm))
    story.append(Paragraph("<b>Output e Raccomandazioni Fornite:</b>", style_body_bold))
    story.append(Paragraph("• 🎯 <b>Scommessa Consigliata:</b> Doppia Chance (1X, X2, 12), Under/Over 2.5, Goal/NoGoal.", style_bullet))
    story.append(Paragraph("• 💰 <b>Probabilità Percentuale di Successo:</b> Es. 85%, 95%.", style_bullet))
    story.append(Paragraph("• ⚡ <b>Livello di Rischio:</b> 🟢 Basso | 🟡 Medio | 🔴 Alto.", style_bullet))
    story.append(Paragraph("• 🧠 <b>Motivazione Tecnica & Commento AI:</b> Dettaglio esplicativo sul perché la combinazione è statisticamente vantaggiosa.", style_bullet))

    add_image_safe("manuale_assets/04_predizioni.png", max_width=174*mm, max_height=80*mm, caption="Interfaccia del Modulo Predizioni con confronto testa a testa e report AI")
    story.append(PageBreak())

    # =========================================================================
    # CAPITOLO 6: AGGIORNAMENTO RISULTATI & WEB SCRAPING
    # =========================================================================
    story.append(Paragraph("6. Modulo Aggiornamento Risultati (Web Scraping Live)", style_h1))
    story.append(Paragraph(
        "Per mantenere l'applicazione costantemente aggiornata senza inserimenti manuali, è integrato un web scraper automatico "
        "multithread che scarica i risultati ufficiali delle 38 giornate di campionato.",
        style_body
    ))
    story.append(Paragraph("<b>Caratteristiche del Web Scraper:</b>", style_body_bold))
    story.append(Paragraph("• <b>Scansione Live a 38 Giornate:</b> Monitora tutti gli incontri, recuperi e posticipi del campionato in corso.", style_bullet))
    story.append(Paragraph("• <b>Aggiornamento Diretto CSV:</b> Rigenera in tempo reale sia il tabellino generale <code>Csv/Campionato.csv</code> sia la tabella riepilogativa <code>Csv/Classifica.csv</code>.", style_bullet))
    story.append(Paragraph("• <b>Pulsante 'Aggiorna Risultati':</b> Accessibile direttamente dal menu principale; a fine download la cache dell'app viene invalidata automaticamente, mostrando i dati freschi senza dover riavviare.", style_bullet))
    story.append(Paragraph("• <b>Rollover di Cambio Stagione Automatico:</b> All'inizio di un nuovo campionato archivia la stagione conclusa in <code>CampionatiPrecedenti.csv</code> e popola le 20 nuove squadre promosse/confermate.", style_bullet))

    add_image_safe("manuale_assets/05_aggiorna.png", max_width=174*mm, max_height=65*mm, caption="Finestra di avanzamento download risultati e sincronizzazione archivi")
    story.append(Spacer(1, 4 * mm))

    # =========================================================================
    # CAPITOLO 7: GESTIONE DATI, PERFORMANCE E RISOLUZIONE PROBLEMI
    # =========================================================================
    story.append(Paragraph("7. Gestione Dati, Performance e Risoluzione Problemi", style_h1))
    story.append(Paragraph(
        "<b>Struttura dei File di Dati (Cartella <code>Csv/</code>):</b>", style_body_bold
    ))
    story.append(Paragraph("• <code>Campionato.csv</code>: Elenco completo di tutte le partite della stagione in corso con data, squadre e punteggi.", style_bullet))
    story.append(Paragraph("• <code>Classifica.csv</code>: Tabella riassuntiva dei punti, partite giocate, vittorie, pareggi, sconfitte e goal.", style_bullet))
    story.append(Paragraph("• <code>CampionatiPrecedenti.csv</code>: Archivio storico aggregato delle ultime stagioni per le predizioni comparative.", style_bullet))
    story.append(Paragraph("• <code>UrlSquadre.csv</code>: Mappatura ufficiale delle 20 squadre con i rispettivi collegamenti web.", style_bullet))

    story.append(Spacer(1, 3 * mm))
    story.append(Paragraph("<b>Comandi Rapidi di Avvio da Terminale:</b>", style_body_bold))
    story.append(Paragraph("<code>&amp; g:/Campionato/venv3.13.1/Scripts/python.exe g:/Campionato/campionato.py</code>", ParagraphStyle('Cmd', parent=style_body, fontName='Courier', fontSize=8.5, textColor=c_navy)))
    story.append(Paragraph("oppure direttamente l'interfaccia principale: <code>.../python.exe app.py</code>", style_body))

    story.append(Spacer(1, 5 * mm))
    story.append(make_callout(
        "In caso di anomalie nei dati, premere il pulsante 'Aggiorna Risultati' nella schermata principale per riscaricare i tabellini ufficiali ed allineare istantaneamente tutti i moduli.",
        bg_color="#ECFDF5", border_color="#10B981", title="CONSIGLIO UTILE"
    ))

    # Costruzione del PDF
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[OK] Manuale generato con successo: {output_pdf}")

if __name__ == '__main__':
    crea_manuale_pdf()
