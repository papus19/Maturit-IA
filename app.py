import streamlit as st
import plotly.graph_objects as go
from supabase import create_client, Client
from urllib.parse import urlencode

# ============================================================
# CONFIGURATION DE LA PAGE
# ============================================================
st.set_page_config(page_title="Diagnostic de Maturité IA", page_icon="🤖", layout="wide")

# CSS global : responsive, titres de questions plus grands, résultat et CTA mis en avant
st.markdown(
    """
    <style>
    /* Conteneur central qui s'ajuste à la taille de l'écran (mobile / tablette / desktop) */
    .block-container {
        max-width: 800px;
        margin: 0 auto;
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }
    .intro-caption {
        font-size: 20px;
        font-weight: 700;
        text-align: center;
        margin-bottom: 10px;
    }
    .question-title {
        font-size: 20px;
        font-weight: 700;
        margin-top: 18px;
        margin-bottom: 4px;
    }
    .score-global {
        font-size: 48px;
        font-weight: 800;
        margin: 10px 0 20px 0;
    }
    .cta-title {
        font-size: 28px;
        font-weight: 800;
        margin-top: 30px;
    }
    .app-footer {
        text-align: center;
        color: gray;
        font-size: 14px;
        margin-top: 40px;
    }
    div[data-testid="stLinkButton"] a {
        font-size: 20px !important;
        font-weight: 700 !important;
        padding: 14px 0 !important;
    }
    @media (max-width: 600px) {
        .score-global { font-size: 34px; }
        .cta-title { font-size: 22px; }
        .intro-caption { font-size: 16px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# En-tête avec logo (affiché sur les deux écrans)
# Logo encodé en base64 directement dans le code : aucun fichier/dossier externe requis.
LOGO_B64 = "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"
st.markdown(
    f"<img src='data:image/png;base64,{LOGO_B64}' width='220'/>",
    unsafe_allow_html=True,
)

# ============================================================
# 1. INITIALISATION DU CLIENT SUPABASE (via les secrets)
# ============================================================
@st.cache_resource
def init_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase_client = init_supabase()

# ============================================================
# 2. DICTIONNAIRE DES QUESTIONS (texte affiché -> valeur 1-4, ou None si "Je ne sais pas")
# ============================================================
NE_SAIS_PAS = "Je ne sais pas"

QUESTIONS = {
    "q1": {
        "label": "Vision de la direction",
        "options": {
            "Pas prioritaire": 1,
            "Intérêt sans budget": 2,
            "Plan annuel avec KPIs": 3,
            "Intégré au modèle d'affaires": 4,
            NE_SAIS_PAS: 0,
        },
    },
    "q2": {
        "label": "Usage des outils LLM",
        "options": {
            "Interdit ou clandestin": 1,
            "Individuel et informel": 2,
            "Formations et ateliers mis en place": 3,
            "Connecté aux flux de travail standardisés": 4,
            NE_SAIS_PAS: 0,
        },
    },
    "q3": {
        "label": "Compétences internes",
        "options": {
            "Aucune compétence": 1,
            "Équipe IT classique": 2,
            "Recours à des consultants/référents": 3,
            "Équipe dédiée Automation/IA": 4,
            NE_SAIS_PAS: 0,
        },
    },
    "q4": {
        "label": "Centralisation des données",
        "options": {
            "Éparpillées (Excel/Local)": 1,
            "Stockage cloud mais extraction manuelle": 2,
            "Centralisées et structurées": 3,
            "Architecture moderne connectée par APIs": 4,
            NE_SAIS_PAS: 0,
        },
    },
    "q5": {
        "label": "Qualité des données",
        "options": {
            "Doublons et erreurs fréquents": 1,
            "Exploitables mais nettoyage manuel lourd": 2,
            "Saisie standardisée et fiable": 3,
            "Pipelines de nettoyage automatisés en continu": 4,
            NE_SAIS_PAS: 0,
        },
    },
    "q6": {
        "label": "Automatisation",
        "options": {
            "Processus manuels": 1,
            "Automatisations basiques isolées": 2,
            "Flux No-Code structurés (n8n/Make)": 3,
            "Flux automatisés intégrant des briques IA/LLM": 4,
            NE_SAIS_PAS: 0,
        },
    },
    "q7": {
        "label": "Avancement des projets",
        "options": {
            "Aucun test": 1,
            "Preuve de Concept (PoC) isolée": 2,
            "Au moins une solution en production": 3,
            "Solutions industrialisées et managées": 4,
            NE_SAIS_PAS: 0,
        },
    },
    "q8": {
        "label": "Identification des opportunités",
        "options": {
            "Inconnue": 1,
            "Réaction ponctuelle du marché": 2,
            "Ateliers d'idéation et scoring ROI": 3,
            "Démarche continue d'audit de processus": 4,
            NE_SAIS_PAS: 0,
        },
    },
    "q9": {
        "label": "Mesure du succès",
        "options": {
            "Subjective": 1,
            "Suivi des coûts sans ROI clair": 2,
            "KPIs opérationnels définis": 3,
            "ROI financier et qualitatif piloté précisément": 4,
            NE_SAIS_PAS: 0,
        },
    },
    "q10": {
        "label": "Confidentialité",
        "options": {
            "Aucune politique": 1,
            "Sensibilisation orale": 2,
            "Charte écrite d'utilisation": 3,
            "Architecture API étanche (non-entraînement des modèles)": 4,
            NE_SAIS_PAS: 0,
        },
    },
    "q11": {
        "label": "Conformité",
        "options": {
            "Partielle / Non mesurée": 1,
            "Respect des bases sans audit des outils d'IA": 2,
            "Cadre Privacy by Design appliqué": 3,
            "Gouvernance des données auditée et transparente": 4,
            NE_SAIS_PAS: 0,
        },
    },
}

Q12_OPTIONS = [
    "Manque de budget",
    "Manque de compétences",
    "Qualité des données",
    "Résistance au changement",
]

PILLARS = {
    "strategie": ["q1", "q2", "q3"],
    "donnees": ["q4", "q5", "q6"],
    "processus": ["q7", "q8", "q9"],
    "gouvernance": ["q10", "q11"],
}


# ============================================================
# 3. LOGIQUE MÉTIER
# ============================================================
def moyenne_pilier(reponses: dict, questions_ids: list) -> float:
    """Moyenne simple des réponses du pilier. 'Je ne sais pas' vaut 0 et tire
    donc la moyenne du pilier vers le bas, comme un signal de faible maturité."""
    return sum(reponses[q] for q in questions_ids) / len(questions_ids)


def calculer_scores(reponses: dict) -> dict:
    score_strategie = moyenne_pilier(reponses, PILLARS["strategie"])
    score_donnees = moyenne_pilier(reponses, PILLARS["donnees"])
    score_processus = moyenne_pilier(reponses, PILLARS["processus"])
    score_gouvernance = moyenne_pilier(reponses, PILLARS["gouvernance"])

    score_global = (score_strategie + score_donnees + score_processus + score_gouvernance) / 4

    if score_global < 2.0:
        segment = "Explorateur"
    elif score_global < 3.0:
        segment = "Expérimentateur"
    elif score_global < 4.0:
        segment = "Opérationnel"
    else:
        segment = "Stratégique"

    return {
        "score_strategie": round(score_strategie, 2),
        "score_donnees": round(score_donnees, 2),
        "score_processus": round(score_processus, 2),
        "score_gouvernance": round(score_gouvernance, 2),
        "score_global": round(score_global, 2),
        "segment": segment,
    }


def enregistrer_lead(infos: dict, reponses: dict, resultats: dict, newsletter_opt_in: bool, est_habilite: bool):
    payload = {
        "firstname": infos["firstname"],
        "lastname": infos["lastname"],
        "email": infos["email"],
        "company": infos["company"],
        "score_strategie": resultats["score_strategie"],
        "score_donnees": resultats["score_donnees"],
        "score_processus": resultats["score_processus"],
        "score_gouvernance": resultats["score_gouvernance"],
        "score_global": resultats["score_global"],
        "segment_maturite": resultats["segment"],
        "pain_point_q12": infos["q12"],
        "raw_responses": reponses,
        "newsletter_opt_in": newsletter_opt_in,
        "est_habilite": est_habilite,
    }
    supabase_client.table("leads_maturite_ia").insert(payload, returning="minimal").execute()


def construire_lien_calendly(res: dict) -> str:
    """Construit un lien Calendly pré-rempli avec le nom, l'email et un résumé du
    résultat, pour que l'équipe commerciale puisse préparer le rendez-vous.
    Le résumé est passé en 'a1' : si votre événement Calendly a une question
    personnalisée (ex: 'Contexte'), elle sera pré-remplie automatiquement."""
    base_url = "https://calendly.com/infosmokafad/30min"
    resume = (
        f"Entreprise: {res['company']} | "
        f"Score global: {res['score_global']:.2f}/4.00 | "
        f"Segment: {res['segment']}"
    )
    params = {
        "name": f"{res['firstname']} {res['lastname']}",
        "email": res["email"],
        "a1": resume,
    }
    return f"{base_url}?{urlencode(params)}"


def est_doublon(firstname: str, lastname: str, email: str, company: str) -> bool:
    """Vérifie via une fonction Supabase (RPC sécurisée) si ce prospect a déjà répondu."""
    result = supabase_client.rpc(
        "check_duplicate_lead",
        {
            "p_firstname": firstname,
            "p_lastname": lastname,
            "p_email": email,
            "p_company": company,
        },
    ).execute()
    return bool(result.data)


def afficher_question(qid: str):
    """Affiche le titre en gros puis le champ radio (label natif masqué)."""
    q = QUESTIONS[qid]
    st.markdown(f"<div class='question-title'>{q['label']}</div>", unsafe_allow_html=True)
    choix = st.radio(
        q["label"],
        list(q["options"].keys()),
        key=qid,
        label_visibility="collapsed",
    )
    return q["options"][choix]


# ============================================================
# 4. ÉTAT DE SESSION
# ============================================================
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "results_data" not in st.session_state:
    st.session_state.results_data = None

# ============================================================
# ÉCRAN 1 : LE QUESTIONNAIRE
# ============================================================
if not st.session_state.submitted:
    st.title("Évaluez la Maturité IA de votre Entreprise")
    st.markdown(
        "<div class='intro-caption'>12 questions rapides · résultat immédiat · 100% confidentiel</div>",
        unsafe_allow_html=True,
    )
    st.caption("Merci de répondre au mieux de vos connaissances.")

    with st.form("diagnostic_form"):
        reponses = {}

        st.markdown(
            "<div class='question-title'>Êtes-vous la personne habilitée à répondre à ces questions "
            "au sein de votre entreprise ?</div>",
            unsafe_allow_html=True,
        )
        habilite = st.radio(
            "Êtes-vous la personne habilitée à répondre à ces questions ?",
            ["Oui", "Non"],
            key="habilite",
            label_visibility="collapsed",
        )
        st.markdown("---")

        st.subheader("Pilier 1 — Stratégie, Culture & Compétences")
        for qid in PILLARS["strategie"]:
            reponses[qid] = afficher_question(qid)

        st.subheader("Pilier 2 — Données & Infrastructure")
        for qid in PILLARS["donnees"]:
            reponses[qid] = afficher_question(qid)

        st.subheader("Pilier 3 — Cas d'Usage & Processus Métiers")
        for qid in PILLARS["processus"]:
            reponses[qid] = afficher_question(qid)

        st.subheader("Pilier 4 — Gouvernance, Sécurité & Éthique")
        for qid in PILLARS["gouvernance"]:
            reponses[qid] = afficher_question(qid)

        st.subheader("Qualification commerciale")
        st.markdown("<div class='question-title'>Quel est votre principal frein ?</div>", unsafe_allow_html=True)
        q12 = st.selectbox(
            "Quel est votre principal frein ?", Q12_OPTIONS, key="q12", label_visibility="collapsed"
        )

        st.subheader("Vos coordonnées")
        col1, col2 = st.columns(2)
        with col1:
            firstname = st.text_input("Prénom *")
        with col2:
            lastname = st.text_input("Nom *")
        email = st.text_input("Email professionnel *")
        company = st.text_input("Entreprise *")

        st.markdown("---")
        newsletter_opt_in = st.checkbox(
            "**Je souhaite recevoir la newsletter avec des conseils et actualités sur l'IA "
            "(vous pourrez vous désabonner à tout moment).**"
        )

        submit = st.form_submit_button("Voir mes résultats en direct", use_container_width=True)

        if submit:
            # 1. Validation des champs obligatoires
            if not all([firstname, lastname, email, company]):
                st.error("Merci de remplir tous les champs obligatoires (*).")
            elif "@" not in email:
                st.error("Merci de saisir un email valide.")
            else:
                # 2. Vérification de doublon (même nom, prénom, email, entreprise)
                # --- TEMPORAIREMENT DÉSACTIVÉE (à retraiter plus tard) ---
                # Pour réactiver : décommenter le bloc ci-dessous et supprimer les 2 lignes
                # "doublon = False" / "verification_ok = True" juste en dessous.
                #
                # try:
                #     doublon = est_doublon(firstname, lastname, email, company)
                #     verification_ok = True
                # except Exception as e:
                #     doublon = None
                #     verification_ok = False
                #     st.error(
                #         "Impossible de vérifier si vous avez déjà répondu (erreur technique). "
                #         f"Merci de réessayer dans un instant.\n\nDétail : {e}"
                #     )
                doublon = False
                verification_ok = True

                if verification_ok and doublon:
                    st.warning(
                        "Vous avez déjà répondu à ce diagnostic avec ces informations "
                        "(même nom, prénom, email et entreprise). Merci de votre participation !"
                    )
                elif verification_ok and not doublon:
                    resultats = calculer_scores(reponses)
                    infos = {
                        "firstname": firstname,
                        "lastname": lastname,
                        "email": email,
                        "company": company,
                        "q12": q12,
                    }
                    try:
                        enregistrer_lead(
                            infos, reponses, resultats, newsletter_opt_in, habilite == "Oui"
                        )
                        st.session_state.save_status = ("success", None)
                    except Exception as e:
                        st.session_state.save_status = ("error", str(e))

                    # Rappel non bloquant si la personne n'est pas habilitée
                    st.session_state.habilite_notice = habilite == "Non"

                    st.session_state.results_data = {
                        "p1": resultats["score_strategie"],
                        "p2": resultats["score_donnees"],
                        "p3": resultats["score_processus"],
                        "p4": resultats["score_gouvernance"],
                        "score_global": resultats["score_global"],
                        "segment": resultats["segment"],
                        "firstname": firstname,
                        "lastname": lastname,
                        "email": email,
                        "company": company,
                    }
                    st.session_state.submitted = True
                    st.rerun()
                # si verification_ok est False, on ne fait rien de plus : l'erreur est déjà affichée
                # et rien n'est enregistré (pas de rerun, le message reste visible).

# ============================================================
# ÉCRAN 2 : RESTITUTION DES RÉSULTATS
# ============================================================
else:
    res = st.session_state.results_data

    # Affichage persistant du statut d'enregistrement (visible même après rerun)
    status = st.session_state.get("save_status")
    if status:
        kind, error_msg = status
        if kind == "success":
            st.success("✅ Vos informations ont bien été enregistrées.")
        else:
            st.error(f"⚠️ L'enregistrement a échoué : {error_msg}")

    # Rappel non bloquant si la personne n'était pas habilitée
    if st.session_state.get("habilite_notice"):
        st.info(
            "💡 Pensez à transmettre ce diagnostic à la personne habilitée à répondre "
            "au nom de l'entreprise, pour un résultat encore plus précis."
        )

    st.title(f"Votre Profil : {res['segment']}")
    st.markdown(
        f"<div class='score-global'>{res['score_global']:.2f} / 4.00</div>",
        unsafe_allow_html=True,
    )

    categories = [
        "Stratégie & Culture",
        "Données & Infra",
        "Cas d'Usage & Processus",
        "Gouvernance & Sécurité",
    ]

    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            r=[res["p1"], res["p2"], res["p3"], res["p4"]],
            theta=categories,
            fill="toself",
            name="Votre score",
        )
    )
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 4])),
        showlegend=False,
        margin=dict(l=40, r=40, t=20, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div class='cta-title'>Étape suivante : débloquez votre plan d'action</div>", unsafe_allow_html=True)
    st.link_button(
        "Réserver mon atelier de cadrage gratuit (30 min)",
        construire_lien_calendly(res),
        use_container_width=True,
    )

    if st.button("Refaire le diagnostic"):
        st.session_state.submitted = False
        st.session_state.results_data = None
        st.session_state.save_status = None
        st.session_state.habilite_notice = False
        st.rerun()

# ============================================================
# PIED DE PAGE (visible sur les deux écrans)
# ============================================================
st.markdown(
    "<div class='app-footer'>📧 Une question ? Écrivez-nous à "
    "<a href='mailto:contact@mokafad.ca'>contact@mokafad.ca</a></div>",
    unsafe_allow_html=True,
)
