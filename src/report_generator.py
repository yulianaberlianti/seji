"""PDF Report Generator for SEJI Platform. v3.0"""

import streamlit as st
import io
import os
import sys
from datetime import date
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data import get_indonesia_3t_data, PRIORITY_COLORS


def _bar_ascii(val, max_val=100, width=20):
    filled = int(val / max_val * width)
    return "█" * filled + "░" * (width - filled)


def generate_pdf_bytes(province_filter, include_sections):
    """Generate PDF report using reportlab."""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.units import cm
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                        Table, TableStyle, HRFlowable, PageBreak)
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    except ImportError:
        return None, "reportlab tidak terinstall. Jalankan: pip install reportlab"

    df = get_indonesia_3t_data()
    if province_filter != "Semua Provinsi":
        df_show = df[df["province"] == province_filter]
    else:
        df_show = df

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2.5*cm, bottomMargin=2*cm,
        title="SEJI Report",
    )

    # Colors
    GOLD   = colors.HexColor("#F5A623")
    DARK   = colors.HexColor("#0D1F38")
    TEAL   = colors.HexColor("#00C4B4")
    RED    = colors.HexColor("#FF4560")
    GRAY   = colors.HexColor("#6B7E96")
    LGRAY  = colors.HexColor("#EDF2F9")
    WHITE  = colors.white

    PC = {
        "Critical": colors.HexColor("#FF4560"),
        "High":     colors.HexColor("#F5A623"),
        "Moderate": colors.HexColor("#00B4A6"),
        "Low":      colors.HexColor("#39D353"),
    }

    styles = getSampleStyleSheet()

    def style(name, **kwargs):
        return ParagraphStyle(name, parent=styles["Normal"], **kwargs)

    title_style   = style("Title",    fontSize=20, textColor=GOLD, spaceAfter=4, alignment=TA_CENTER, fontName="Helvetica-Bold")
    sub_style     = style("Sub",      fontSize=10, textColor=GRAY, spaceAfter=2, alignment=TA_CENTER)
    h1_style      = style("H1",       fontSize=13, textColor=DARK, spaceBefore=14, spaceAfter=6, fontName="Helvetica-Bold")
    h2_style      = style("H2",       fontSize=11, textColor=TEAL, spaceBefore=10, spaceAfter=4, fontName="Helvetica-Bold")
    body_style    = style("Body",     fontSize=9,  textColor=DARK, spaceAfter=4, leading=14)
    caption_style = style("Caption",  fontSize=8,  textColor=GRAY, spaceAfter=2, alignment=TA_CENTER)
    bold_style    = style("Bold",     fontSize=9,  textColor=DARK, fontName="Helvetica-Bold")

    story = []

    # ── Cover ─────────────────────────────────────────────────────
    story.append(Spacer(1, 1.5*cm))
    story.append(Paragraph("SOLAR ENERGY JUSTICE INDEX", title_style))
    story.append(Paragraph("Laporan Analisis Prioritas PLTS Indonesia", sub_style))
    story.append(Spacer(1, 0.3*cm))
    scope = province_filter if province_filter != "Semua Provinsi" else "Seluruh Indonesia"
    story.append(Paragraph(f"Wilayah: {scope}", sub_style))
    story.append(Paragraph(f"Tanggal: {date.today().strftime('%d %B %Y')}", sub_style))
    story.append(HRFlowable(width="100%", thickness=2, color=GOLD, spaceAfter=14))
    story.append(Spacer(1, 0.5*cm))

    # ── Executive Summary ─────────────────────────────────────────
    if "executive_summary" in include_sections:
        story.append(Paragraph("1. RINGKASAN EKSEKUTIF", h1_style))
        story.append(HRFlowable(width="100%", thickness=1, color=LGRAY, spaceAfter=8))

        total    = len(df_show)
        critical = int((df_show["priority"] == "Critical").sum())
        high_p   = int((df_show["priority"] == "High").sum())
        t3_count = int(df_show["is_3t"].sum())
        avg_solar= df_show["solar_kwh"].mean()
        avg_acc  = df_show["electricity_access"].mean() * 100
        avg_seji = df_show["seji_score"].mean()

        summary_data = [
            ["Metrik", "Nilai", "Keterangan"],
            ["Total Provinsi Dianalisis", str(total), "Seluruh provinsi dalam cakupan"],
            ["Wilayah 3T (Tertinggal)", f"{t3_count} ({t3_count/max(total,1)*100:.0f}%)", "Tertinggal, Terdepan, Terluar"],
            ["Prioritas CRITICAL", str(critical), "SEJI Score > 75 — intervensi segera"],
            ["Prioritas HIGH",     str(high_p),   "SEJI Score 55–75 — perlu perencanaan"],
            ["SEJI Score Rata-rata", f"{avg_seji:.1f}/100", "Skor keadilan energi rata-rata"],
            ["Radiasi Rata-rata",  f"{avg_solar:.2f} kWh/m²/hari", "Data NASA POWER"],
            ["Akses Listrik Avg",  f"{avg_acc:.1f}%", "Rasio elektrifikasi BPS 2023"],
        ]
        tbl = Table(summary_data, colWidths=[5.5*cm, 3.5*cm, 8*cm])
        tbl.setStyle(TableStyle([
            ("BACKGROUND",  (0, 0), (-1, 0),  DARK),
            ("TEXTCOLOR",   (0, 0), (-1, 0),  WHITE),
            ("FONTNAME",    (0, 0), (-1, 0),  "Helvetica-Bold"),
            ("FONTSIZE",    (0, 0), (-1, 0),  9),
            ("BACKGROUND",  (0, 1), (-1, -1), LGRAY),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LGRAY]),
            ("FONTSIZE",    (0, 1), (-1, -1), 8),
            ("GRID",        (0, 0), (-1, -1), 0.5, colors.HexColor("#D0D8E8")),
            ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING",  (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING",(0, 0),(-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ]))
        story.append(tbl)
        story.append(Spacer(1, 0.5*cm))

        top1 = df.iloc[0]
        story.append(Paragraph("Temuan Utama:", h2_style))
        story.append(Paragraph(
            f"<b>{top1['province']}</b> menempati peringkat SEJI tertinggi "
            f"({top1['seji_score']:.1f}/100) — kombinasi radiasi surya "
            f"{top1['solar_kwh']:.1f} kWh/m²/hari, akses listrik hanya "
            f"{top1['electricity_access']*100:.0f}%, dan kemiskinan "
            f"{top1['poverty_rate']:.1f}%. Wilayah ini adalah kandidat utama "
            f"instalasi PLTS off-grid terdesentralisasi.",
            body_style
        ))

    # ── Priority Ranking ──────────────────────────────────────────
    if "priority_ranking" in include_sections:
        story.append(PageBreak())
        story.append(Paragraph("2. RANKING PRIORITAS SEJI", h1_style))
        story.append(HRFlowable(width="100%", thickness=1, color=LGRAY, spaceAfter=8))
        story.append(Paragraph("Tabel berikut menampilkan ranking provinsi berdasarkan SEJI Score (tertinggi = prioritas utama).", body_style))

        top_n = df_show.head(20)
        rank_data = [["Rank", "Provinsi", "Kepulauan", "SEJI", "Prioritas", "Solar (kWh/m²)", "Akses (%)", "Miskin (%)"]]
        for i, (_, r) in enumerate(top_n.iterrows(), 1):
            rank_data.append([
                str(i),
                r["province"],
                r["island"],
                f"{r['seji_score']:.1f}",
                str(r["priority"]),
                f"{r['solar_kwh']:.2f}",
                f"{r['electricity_access']*100:.1f}",
                f"{r['poverty_rate']:.1f}",
            ])

        tbl2 = Table(rank_data, colWidths=[1*cm, 4.5*cm, 3*cm, 1.5*cm, 2*cm, 2.2*cm, 2*cm, 1.8*cm])
        style_cmds = [
            ("BACKGROUND",  (0, 0), (-1, 0),   DARK),
            ("TEXTCOLOR",   (0, 0), (-1, 0),   WHITE),
            ("FONTNAME",    (0, 0), (-1, 0),   "Helvetica-Bold"),
            ("FONTSIZE",    (0, 0), (-1, -1),  7.5),
            ("GRID",        (0, 0), (-1, -1),  0.5, colors.HexColor("#D0D8E8")),
            ("VALIGN",      (0, 0), (-1, -1),  "MIDDLE"),
            ("TOPPADDING",  (0, 0), (-1, -1),  4),
            ("BOTTOMPADDING",(0, 0),(-1, -1),  4),
            ("LEFTPADDING", (0, 0), (-1, -1),  5),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LGRAY]),
        ]
        # Color priority column
        for i, (_, r) in enumerate(top_n.iterrows(), 1):
            pc = PC.get(str(r["priority"]), GRAY)
            style_cmds.append(("TEXTCOLOR", (4, i), (4, i), pc))
            style_cmds.append(("FONTNAME",  (4, i), (4, i), "Helvetica-Bold"))
        tbl2.setStyle(TableStyle(style_cmds))
        story.append(tbl2)

    # ── Critical regions detail ───────────────────────────────────
    if "critical_detail" in include_sections:
        critical_df = df_show[df_show["priority"] == "Critical"]
        if len(critical_df) > 0:
            story.append(PageBreak())
            story.append(Paragraph("3. DETAIL WILAYAH PRIORITAS KRITIS", h1_style))
            story.append(HRFlowable(width="100%", thickness=1, color=LGRAY, spaceAfter=8))
            story.append(Paragraph(
                f"Terdapat {len(critical_df)} wilayah dengan status CRITICAL (SEJI > 75) "
                f"yang membutuhkan intervensi segera.",
                body_style
            ))
            story.append(Spacer(1, 0.3*cm))

            for _, r in critical_df.iterrows():
                story.append(Paragraph(f"▶ {r['province']} ({r['island']})", h2_style))
                detail_data = [
                    ["Parameter", "Nilai", "Status"],
                    ["SEJI Score",         f"{r['seji_score']:.1f}/100", "CRITICAL"],
                    ["Radiasi Matahari",   f"{r['solar_kwh']:.2f} kWh/m²/hari", "Tinggi → Peluang"],
                    ["Akses Listrik",      f"{r['electricity_access']*100:.1f}%", "Rendah → Masalah"],
                    ["Tingkat Kemiskinan", f"{r['poverty_rate']:.1f}%", "Tinggi → Kerentanan"],
                    ["Keterpencilan",      f"{r['remoteness']:.3f}", "Tinggi" if r["remoteness"]>0.6 else "Sedang"],
                    ["Status 3T",          "Ya" if r["is_3t"] else "Tidak", "—"],
                ]
                dtbl = Table(detail_data, colWidths=[5*cm, 4*cm, 8*cm])
                dtbl.setStyle(TableStyle([
                    ("BACKGROUND",  (0, 0), (-1, 0),  colors.HexColor("#FF4560")),
                    ("TEXTCOLOR",   (0, 0), (-1, 0),  WHITE),
                    ("FONTNAME",    (0, 0), (-1, 0),  "Helvetica-Bold"),
                    ("FONTSIZE",    (0, 0), (-1, -1), 8),
                    ("GRID",        (0, 0), (-1, -1), 0.5, colors.HexColor("#D0D8E8")),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LGRAY]),
                    ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
                    ("TOPPADDING",  (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0,0),(-1,-1),  4),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ]))
                story.append(dtbl)
                story.append(Spacer(1, 0.35*cm))
                story.append(Paragraph(
                    "Rekomendasi: Instalasi PLTS off-grid komunal segera (100–500 kWp). "
                    "Prioritaskan dalam APBN/APBD jangka pendek. Pertimbangkan skema "
                    "pendanaan hijau (green bond) dan kemitraan KPBU.",
                    body_style
                ))
                story.append(Spacer(1, 0.2*cm))

    # ── Methodology ──────────────────────────────────────────────
    if "methodology" in include_sections:
        story.append(PageBreak())
        story.append(Paragraph("4. METODOLOGI", h1_style))
        story.append(HRFlowable(width="100%", thickness=1, color=LGRAY, spaceAfter=8))
        story.append(Paragraph("Formula SEJI:", h2_style))
        story.append(Paragraph(
            "SEJI = w1*Solar_norm + w2*(1 - EnergyAccess_norm) + w3*Poverty_norm + "
            "w4*Population_norm + w5*Remoteness_norm",
            bold_style
        ))
        story.append(Spacer(1, 0.3*cm))

        meth_data = [
            ["Parameter", "Bobot (AHP)", "Sumber Data", "Satuan"],
            ["Solar Potential",  "0.30", "NASA POWER / GSA", "kWh/m²/hari"],
            ["Energy Access",    "0.30", "VIIRS DNB / BPS",  "rasio 0-1"],
            ["Poverty Rate",     "0.20", "BPS 2023",         "%"],
            ["Population Density","0.10","WorldPop",         "jiwa/km²"],
            ["Remoteness",       "0.10", "OSM / BIG",        "indeks 0-1"],
        ]
        mtbl = Table(meth_data, colWidths=[5*cm, 2.5*cm, 5*cm, 4.5*cm])
        mtbl.setStyle(TableStyle([
            ("BACKGROUND",  (0, 0), (-1, 0),  DARK),
            ("TEXTCOLOR",   (0, 0), (-1, 0),  WHITE),
            ("FONTNAME",    (0, 0), (-1, 0),  "Helvetica-Bold"),
            ("FONTSIZE",    (0, 0), (-1, -1), 8),
            ("GRID",        (0, 0), (-1, -1), 0.5, colors.HexColor("#D0D8E8")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LGRAY]),
            ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING",  (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING",(0, 0),(-1,-1),  4),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(mtbl)
        story.append(Spacer(1, 0.5*cm))
        story.append(Paragraph("Referensi:", h2_style))
        refs = [
            "IRENA, 2023. Renewable Power Generation Costs in 2022.",
            "ESDM, 2022. Rencana Umum Energi Nasional (RUEN).",
            "Sovacool et al., 2017. Energy Justice: A Conceptual Review.",
            "Kumar et al., 2020. GIS-based multi-criteria solar energy potential analysis.",
        ]
        for ref in refs:
            story.append(Paragraph(f"• {ref}", body_style))

    # ── Footer ────────────────────────────────────────────────────
    story.append(Spacer(1, 1*cm))
    story.append(HRFlowable(width="100%", thickness=1, color=GOLD, spaceAfter=6))
    story.append(Paragraph(
        f"Laporan ini dibuat secara otomatis oleh SEJI Platform v3.0 · {date.today().strftime('%d/%m/%Y')} · "
        "Data bersifat simulasi untuk keperluan riset dan perencanaan kebijakan.",
        caption_style
    ))

    doc.build(story)
    buf.seek(0)
    return buf.read(), None


def show():
    df = get_indonesia_3t_data()
    cc = st.session_state.get("cc", {})

    st.markdown("""
    <div class="hero-banner" style="padding:1.4rem 2.2rem;">
        <span class="badge">📄 REPORT GENERATOR</span>
        <h2 class="hero-title" style="font-size:1.55rem;">PDF Report Generator</h2>
        <p class="hero-subtitle">Ekspor laporan ringkas SEJI ke PDF — siap untuk presentasi, pemerintah, atau akademisi</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Config ────────────────────────────────────────────────────
    col_cfg, col_prev = st.columns([1, 2])

    with col_cfg:
        st.markdown("### ⚙️ Konfigurasi Laporan")

        prov_opts = ["Semua Provinsi"] + sorted(df["province"].tolist())
        report_scope = st.selectbox("Cakupan Laporan", prov_opts)

        st.markdown("**Bagian yang Disertakan:**")
        sec_exec   = st.checkbox("📋 Ringkasan Eksekutif",  value=True)
        sec_rank   = st.checkbox("📊 Ranking Prioritas",    value=True)
        sec_crit   = st.checkbox("🚨 Detail Wilayah Kritis", value=True)
        sec_meth   = st.checkbox("📐 Metodologi & Referensi", value=True)

        sections = []
        if sec_exec: sections.append("executive_summary")
        if sec_rank: sections.append("priority_ranking")
        if sec_crit: sections.append("critical_detail")
        if sec_meth: sections.append("methodology")

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("📄 Generate PDF Report", use_container_width=True):
            with st.spinner("Membuat PDF..."):
                pdf_bytes, error = generate_pdf_bytes(report_scope, sections)
            if error:
                st.error(f"Error: {error}")
                st.info("Coba install reportlab: `pip install reportlab`")
            elif pdf_bytes:
                scope_label = report_scope.replace(" ", "_") if report_scope != "Semua Provinsi" else "Indonesia"
                filename = f"SEJI_Report_{scope_label}_{date.today().strftime('%Y%m%d')}.pdf"
                st.download_button(
                    label="⬇️ Download PDF",
                    data=pdf_bytes,
                    file_name=filename,
                    mime="application/pdf",
                    use_container_width=True,
                )
                st.success("✅ PDF berhasil dibuat! Klik tombol di atas untuk mengunduh.")

    with col_prev:
        st.markdown("### 👁️ Preview Konten Laporan")

        scope = report_scope if report_scope != "Semua Provinsi" else "Seluruh Indonesia"
        df_show = df if report_scope == "Semua Provinsi" else df[df["province"] == report_scope]

        total    = len(df_show)
        critical = int((df_show["priority"] == "Critical").sum())
        high_p   = int((df_show["priority"] == "High").sum())
        avg_seji = df_show["seji_score"].mean() if total > 0 else 0

        st.markdown(f"""
        <div style='background:var(--bg-card);border:1px solid rgba(245,166,35,0.28);
                    border-radius:14px;padding:1.4rem;'>
            <div style='font-size:0.65rem;color:#F5A623;font-weight:700;
                        font-family:Space Mono;letter-spacing:2px;'>PREVIEW — SEJI REPORT</div>
            <div style='font-size:1.1rem;font-weight:700;color:var(--text-primary);margin:6px 0;'>
                Solar Energy Justice Index</div>
            <div style='font-size:0.78rem;color:var(--text-muted);margin-bottom:10px;'>
                Wilayah: {scope} · {date.today().strftime('%d %B %Y')}</div>
            <hr style='border:none;border-top:1px solid rgba(245,166,35,0.2);margin:8px 0;'>
        """, unsafe_allow_html=True)

        if sec_exec:
            st.markdown(f"""
            <div style='margin-bottom:8px;'>
                <div style='font-size:0.72rem;color:#F5A623;font-weight:700;'>1. RINGKASAN EKSEKUTIF</div>
                <div style='font-size:0.78rem;color:var(--text-secondary);line-height:1.6;'>
                    • Total provinsi: {total} | Wilayah 3T: {int(df_show["is_3t"].sum())}<br>
                    • Prioritas CRITICAL: {critical} | HIGH: {high_p}<br>
                    • Rata-rata SEJI: {avg_seji:.1f}/100
                </div>
            </div>""", unsafe_allow_html=True)

        if sec_rank:
            st.markdown("""
            <div style='margin-bottom:8px;'>
                <div style='font-size:0.72rem;color:#F5A623;font-weight:700;'>2. RANKING PRIORITAS</div>
                <div style='font-size:0.78rem;color:var(--text-secondary);'>
                    Tabel ranking top-20 provinsi berdasarkan SEJI Score</div>
            </div>""", unsafe_allow_html=True)

        if sec_crit:
            crit_df = df_show[df_show["priority"] == "Critical"]
            prov_list = ", ".join(crit_df["province"].tolist()[:5])
            if len(crit_df) > 5:
                prov_list += f"... (+{len(crit_df)-5} lainnya)"
            st.markdown(f"""
            <div style='margin-bottom:8px;'>
                <div style='font-size:0.72rem;color:#FF4560;font-weight:700;'>3. DETAIL KRITIS ({len(crit_df)} wilayah)</div>
                <div style='font-size:0.78rem;color:var(--text-secondary);'>{prov_list or "Tidak ada wilayah kritis"}</div>
            </div>""", unsafe_allow_html=True)

        if sec_meth:
            st.markdown("""
            <div style='margin-bottom:8px;'>
                <div style='font-size:0.72rem;color:#00C4B4;font-weight:700;'>4. METODOLOGI & REFERENSI</div>
                <div style='font-size:0.78rem;color:var(--text-secondary);'>
                    Formula SEJI, bobot AHP, sumber data, daftar pustaka</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # Top 5 preview table
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**Top 5 Provinsi Prioritas:**")
        top5 = df_show.head(5)[["province", "seji_score", "priority", "solar_kwh", "electricity_access"]].copy()
        top5["electricity_access"] = (top5["electricity_access"] * 100).round(1).astype(str) + "%"
        top5.columns = ["Provinsi", "SEJI", "Prioritas", "Solar (kWh/m²)", "Akses Listrik"]
        st.dataframe(top5.reset_index(drop=True), use_container_width=True,
                     column_config={"SEJI": st.column_config.ProgressColumn("SEJI", min_value=0, max_value=100, format="%.1f")})

    # ── Template options ──────────────────────────────────────────
    st.markdown("### 📌 Catatan Penggunaan")
    n1, n2, n3 = st.columns(3)
    with n1:
        st.markdown("""<div class="info-card">
        <h4>🏛️ Untuk Pemerintah</h4>
        <p>Laporan ini siap digunakan dalam rapat koordinasi lintas kementerian atau
        penyusunan proposal anggaran APBN/APBD untuk program PLTS 3T.</p>
        </div>""", unsafe_allow_html=True)
    with n2:
        st.markdown("""<div class="info-card">
        <h4>🎓 Untuk Akademisi</h4>
        <p>Data dan metodologi SEJI menggunakan pendekatan MCDA/AHP yang
        dapat dikutip sebagai referensi riset energi terbarukan dan keadilan energi.</p>
        </div>""", unsafe_allow_html=True)
    with n3:
        st.markdown("""<div class="info-card">
        <h4>💼 Untuk Investor</h4>
        <p>Identifikasi peluang investasi PLTS berbasis data spasial dan indeks kerentanan
        energi yang terukur dan objektif.</p>
        </div>""", unsafe_allow_html=True)
