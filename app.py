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
st.image("assets/logo-mokafad.png", width=220)

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