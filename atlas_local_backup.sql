--
-- PostgreSQL database dump
--

\restrict a67JRawDB9CxGZtw0VEJduZkmwbyvvwrHACgXznqqQ0pNlJWju5uwFgIZba0bhJ

-- Dumped from database version 16.11 (Homebrew)
-- Dumped by pg_dump version 16.11 (Homebrew)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: update_investment_plan_updated_at(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.update_investment_plan_updated_at() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


--
-- Name: update_last_updated_column(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.update_last_updated_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.last_updated = NOW();
    RETURN NEW;
END;
$$;


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: apprentissages; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.apprentissages (
    id integer NOT NULL,
    nom character varying(200) NOT NULL,
    description text,
    fichier_pdf character varying(255),
    image character varying(255),
    date_creation timestamp without time zone,
    date_modification timestamp without time zone,
    actif boolean,
    ordre integer,
    fichier_pdf_original character varying(255)
);


--
-- Name: apprentissages_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.apprentissages_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: apprentissages_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.apprentissages_id_seq OWNED BY public.apprentissages.id;


--
-- Name: credits; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.credits (
    id integer NOT NULL,
    investor_profile_id integer,
    credit_type character varying(50),
    description character varying(200),
    initial_amount numeric(12,2),
    remaining_amount numeric(12,2),
    interest_rate numeric(5,4),
    duration_years integer,
    monthly_payment numeric(12,2),
    start_date date,
    end_date date,
    type_credit character varying(50),
    montant_initial numeric(12,2),
    montant_restant numeric(12,2),
    taux_interet numeric(5,4),
    duree_mois integer,
    mensualite numeric(12,2),
    date_debut date,
    date_fin date,
    created_date timestamp with time zone DEFAULT now(),
    updated_date timestamp with time zone DEFAULT now(),
    calculated_monthly_payment double precision,
    calculated_remaining_capital double precision,
    last_calculation_date timestamp without time zone
);


--
-- Name: TABLE credits; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.credits IS 'Detailed credit tracking';


--
-- Name: COLUMN credits.calculated_remaining_capital; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.credits.calculated_remaining_capital IS 'Capital restant calculé automatiquement selon amortissement';


--
-- Name: COLUMN credits.last_calculation_date; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.credits.last_calculation_date IS 'Date du dernier calcul automatique';


--
-- Name: credits_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.credits_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: credits_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.credits_id_seq OWNED BY public.credits.id;


--
-- Name: crypto_prices; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.crypto_prices (
    id integer NOT NULL,
    symbol character varying(50) NOT NULL,
    price_usd double precision NOT NULL,
    price_eur double precision NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    created_at timestamp without time zone NOT NULL
);


--
-- Name: crypto_prices_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.crypto_prices_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: crypto_prices_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.crypto_prices_id_seq OWNED BY public.crypto_prices.id;


--
-- Name: investment_plan_lines; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.investment_plan_lines (
    id integer NOT NULL,
    plan_id integer NOT NULL,
    support_envelope character varying(100) NOT NULL,
    description character varying(200) NOT NULL,
    reference character varying(50),
    percentage double precision NOT NULL,
    order_index integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    CONSTRAINT chk_percentage_max CHECK ((percentage <= (100)::double precision)),
    CONSTRAINT chk_percentage_positive CHECK ((percentage >= (0)::double precision))
);


--
-- Name: TABLE investment_plan_lines; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.investment_plan_lines IS 'Lignes de détail des plans d investissement';


--
-- Name: COLUMN investment_plan_lines.support_envelope; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.investment_plan_lines.support_envelope IS 'Type d enveloppe (PEA, Assurance Vie, etc.)';


--
-- Name: COLUMN investment_plan_lines.description; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.investment_plan_lines.description IS 'Description du placement (ex: ETF World)';


--
-- Name: COLUMN investment_plan_lines.reference; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.investment_plan_lines.reference IS 'Référence du placement (ex: ISIN)';


--
-- Name: COLUMN investment_plan_lines.percentage; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.investment_plan_lines.percentage IS 'Pourcentage du montant mensuel à investir';


--
-- Name: COLUMN investment_plan_lines.order_index; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.investment_plan_lines.order_index IS 'Ordre d affichage des lignes';


--
-- Name: investment_plan_lines_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.investment_plan_lines_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: investment_plan_lines_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.investment_plan_lines_id_seq OWNED BY public.investment_plan_lines.id;


--
-- Name: investment_plans; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.investment_plans (
    id integer NOT NULL,
    user_id integer NOT NULL,
    name character varying(100) NOT NULL,
    is_active boolean NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


--
-- Name: TABLE investment_plans; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.investment_plans IS 'Plans d investissement mensuel des utilisateurs';


--
-- Name: COLUMN investment_plans.user_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.investment_plans.user_id IS 'ID de l utilisateur propriétaire du plan';


--
-- Name: COLUMN investment_plans.name; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.investment_plans.name IS 'Nom du plan (par défaut: Plan principal)';


--
-- Name: COLUMN investment_plans.is_active; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.investment_plans.is_active IS 'Indique si le plan est actif';


--
-- Name: investment_plans_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.investment_plans_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: investment_plans_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.investment_plans_id_seq OWNED BY public.investment_plans.id;


--
-- Name: investor_profiles; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.investor_profiles (
    id integer NOT NULL,
    user_id integer,
    monthly_net_income numeric(12,2) DEFAULT 0 NOT NULL,
    monthly_savings_capacity numeric(12,2) DEFAULT 0 NOT NULL,
    current_savings numeric(12,2) DEFAULT 0,
    impots_mensuels numeric(12,2) DEFAULT 0,
    risk_tolerance character varying(20) DEFAULT 'modéré'::character varying,
    investment_experience character varying(20) DEFAULT 'intermédiaire'::character varying,
    investment_goals text,
    investment_horizon character varying(20) DEFAULT 'moyen'::character varying,
    civilite character varying(10),
    date_naissance date,
    lieu_naissance character varying(100),
    nationalite character varying(50),
    pays_residence character varying(50),
    pays_residence_fiscal character varying(50),
    family_situation character varying(30),
    professional_situation character varying(50),
    metier character varying(100),
    objectif_premiers_pas boolean DEFAULT false,
    objectif_constituer_capital boolean DEFAULT false,
    objectif_diversifier boolean DEFAULT false,
    objectif_optimiser_rendement boolean DEFAULT false,
    objectif_preparer_retraite boolean DEFAULT false,
    objectif_securite_financiere boolean DEFAULT false,
    objectif_projet_immobilier boolean DEFAULT false,
    objectif_revenus_complementaires boolean DEFAULT false,
    objectif_transmettre_capital boolean DEFAULT false,
    objectif_proteger_famille boolean DEFAULT false,
    tolerance_risque character varying(20),
    horizon_placement character varying(20),
    besoin_liquidite character varying(30),
    experience_investissement character varying(30),
    attitude_volatilite character varying(30),
    has_livret_a boolean DEFAULT false,
    livret_a_value numeric(12,2) DEFAULT 0,
    has_ldds boolean DEFAULT false,
    ldds_value numeric(12,2) DEFAULT 0,
    has_lep boolean DEFAULT false,
    lep_value numeric(12,2) DEFAULT 0,
    has_pel_cel boolean DEFAULT false,
    pel_cel_value numeric(12,2) DEFAULT 0,
    has_current_account boolean DEFAULT false,
    current_account_value numeric(12,2) DEFAULT 0,
    liquidites_personnalisees_json jsonb,
    has_pea boolean DEFAULT false,
    pea_value numeric(12,2) DEFAULT 0,
    has_per boolean DEFAULT false,
    per_value numeric(12,2) DEFAULT 0,
    has_life_insurance boolean DEFAULT false,
    life_insurance_value numeric(12,2) DEFAULT 0,
    has_pee boolean DEFAULT false,
    pee_value numeric(12,2) DEFAULT 0,
    has_scpi boolean DEFAULT false,
    scpi_value numeric(12,2) DEFAULT 0,
    placements_personnalises_json jsonb,
    has_real_estate boolean DEFAULT false,
    real_estate_value numeric(12,2) DEFAULT 0,
    has_immobilier boolean DEFAULT false,
    immobilier_value numeric(12,2) DEFAULT 0,
    immobilier_data_json jsonb,
    has_autres_biens boolean DEFAULT false,
    autres_biens_value numeric(12,2) DEFAULT 0,
    autres_biens_data_json jsonb,
    cryptomonnaies_data_json jsonb,
    credits_data_json jsonb,
    revenus_complementaires numeric(12,2) DEFAULT 0,
    revenus_complementaires_json jsonb,
    charges_mensuelles numeric(12,2) DEFAULT 0,
    charges_mensuelles_json jsonb,
    has_pel boolean DEFAULT false,
    pel_value numeric(12,2) DEFAULT 0,
    has_cel boolean DEFAULT false,
    cel_value numeric(12,2) DEFAULT 0,
    has_autres_livrets boolean DEFAULT false,
    autres_livrets_value numeric(12,2) DEFAULT 0,
    has_cto boolean DEFAULT false,
    cto_value numeric(12,2) DEFAULT 0,
    has_private_equity boolean DEFAULT false,
    private_equity_value numeric(12,2) DEFAULT 0,
    has_crowdfunding boolean DEFAULT false,
    crowdfunding_value numeric(12,2) DEFAULT 0,
    other_investments text,
    objectif_constitution_epargne boolean DEFAULT false,
    objectif_retraite boolean DEFAULT false,
    objectif_transmission boolean DEFAULT false,
    objectif_defiscalisation boolean DEFAULT false,
    objectif_immobilier boolean DEFAULT false,
    profil_risque_connu boolean DEFAULT false,
    profil_risque_choisi character varying(20),
    question_1_reponse character varying(100),
    question_2_reponse character varying(100),
    question_3_reponse character varying(100),
    question_4_reponse character varying(100),
    question_5_reponse character varying(100),
    synthese_profil_risque character varying(500),
    cryptos_json jsonb,
    liquidites_personnalisees_json_legacy text,
    placements_personnalises_json_legacy text,
    date_completed timestamp with time zone DEFAULT now(),
    last_updated timestamp with time zone DEFAULT now(),
    professional_situation_other character varying(100),
    calculated_total_liquidites double precision DEFAULT 0.0,
    calculated_total_placements double precision DEFAULT 0.0,
    calculated_total_immobilier_net double precision DEFAULT 0.0,
    calculated_total_cryptomonnaies double precision DEFAULT 0.0,
    calculated_total_autres_biens double precision DEFAULT 0.0,
    calculated_total_credits_consommation double precision DEFAULT 0.0,
    calculated_total_actifs double precision DEFAULT 0.0,
    calculated_patrimoine_total_net double precision DEFAULT 0.0,
    last_calculation_date timestamp without time zone,
    CONSTRAINT chk_investment_experience CHECK (((investment_experience)::text = ANY ((ARRAY['débutant'::character varying, 'débutante'::character varying, 'intermédiaire'::character varying, 'intermediaire'::character varying, 'confirmé'::character varying, 'confirmée'::character varying, 'expert'::character varying, 'experte'::character varying, 'debutant'::character varying, 'confirme'::character varying])::text[]))),
    CONSTRAINT chk_investment_horizon CHECK (((investment_horizon)::text = ANY ((ARRAY['court'::character varying, 'court terme'::character varying, 'moyen'::character varying, 'moyen terme'::character varying, 'long'::character varying, 'long terme'::character varying])::text[]))),
    CONSTRAINT chk_risk_tolerance CHECK (((risk_tolerance)::text = ANY ((ARRAY['conservateur'::character varying, 'conservatrice'::character varying, 'modéré'::character varying, 'modérée'::character varying, 'modere'::character varying, 'moderee'::character varying, 'dynamique'::character varying, 'agressif'::character varying, 'agressive'::character varying])::text[])))
);


--
-- Name: TABLE investor_profiles; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.investor_profiles IS 'Detailed financial profiles with JSONB fields for complex data';


--
-- Name: COLUMN investor_profiles.calculated_total_liquidites; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.investor_profiles.calculated_total_liquidites IS 'Total des liquidités calculé et sauvegardé';


--
-- Name: COLUMN investor_profiles.calculated_total_placements; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.investor_profiles.calculated_total_placements IS 'Total des placements financiers calculé et sauvegardé';


--
-- Name: COLUMN investor_profiles.calculated_total_immobilier_net; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.investor_profiles.calculated_total_immobilier_net IS 'Total immobilier net (valeur - crédits immobiliers) calculé et sauvegardé';


--
-- Name: COLUMN investor_profiles.calculated_total_cryptomonnaies; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.investor_profiles.calculated_total_cryptomonnaies IS 'Total des cryptomonnaies avec prix actuels calculé et sauvegardé';


--
-- Name: COLUMN investor_profiles.calculated_total_autres_biens; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.investor_profiles.calculated_total_autres_biens IS 'Total des autres biens calculé et sauvegardé';


--
-- Name: COLUMN investor_profiles.calculated_total_credits_consommation; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.investor_profiles.calculated_total_credits_consommation IS 'Total des crédits de consommation restants calculé et sauvegardé';


--
-- Name: COLUMN investor_profiles.calculated_total_actifs; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.investor_profiles.calculated_total_actifs IS 'Total de tous les actifs calculé et sauvegardé';


--
-- Name: COLUMN investor_profiles.calculated_patrimoine_total_net; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.investor_profiles.calculated_patrimoine_total_net IS 'Patrimoine total net (actifs - crédits) calculé et sauvegardé';


--
-- Name: COLUMN investor_profiles.last_calculation_date; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.investor_profiles.last_calculation_date IS 'Date de dernière mise à jour des calculs patrimoniaux';


--
-- Name: investor_profiles_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.investor_profiles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: investor_profiles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.investor_profiles_id_seq OWNED BY public.investor_profiles.id;


--
-- Name: payment_methods; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.payment_methods (
    id integer NOT NULL,
    user_id integer,
    method_type character varying(20),
    provider character varying(50),
    provider_id character varying(100),
    is_default boolean DEFAULT false,
    is_active boolean DEFAULT true,
    created_date timestamp with time zone DEFAULT now()
);


--
-- Name: TABLE payment_methods; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.payment_methods IS 'User payment method management';


--
-- Name: payment_methods_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.payment_methods_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: payment_methods_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.payment_methods_id_seq OWNED BY public.payment_methods.id;


--
-- Name: portfolio_holdings; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.portfolio_holdings (
    id integer NOT NULL,
    portfolio_id integer,
    asset_type character varying(50),
    symbol character varying(20),
    quantity numeric(15,8),
    purchase_price numeric(12,4),
    current_price numeric(12,4),
    purchase_date timestamp with time zone,
    last_updated timestamp with time zone DEFAULT now()
);


--
-- Name: portfolio_holdings_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.portfolio_holdings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: portfolio_holdings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.portfolio_holdings_id_seq OWNED BY public.portfolio_holdings.id;


--
-- Name: portfolios; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.portfolios (
    id integer NOT NULL,
    user_id integer,
    name character varying(100) NOT NULL,
    strategy character varying(50),
    total_value numeric(15,2) DEFAULT 0,
    created_date timestamp with time zone DEFAULT now(),
    last_updated timestamp with time zone DEFAULT now(),
    cash_amount numeric(15,2) DEFAULT 0.0,
    invested_amount numeric(15,2) DEFAULT 0.0,
    monthly_contribution numeric(15,2) DEFAULT 0.0,
    target_allocation text
);


--
-- Name: TABLE portfolios; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.portfolios IS 'Investment portfolios for users';


--
-- Name: portfolios_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.portfolios_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: portfolios_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.portfolios_id_seq OWNED BY public.portfolios.id;


--
-- Name: subscriptions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.subscriptions (
    id integer NOT NULL,
    user_id integer,
    status character varying(20) DEFAULT 'trial'::character varying,
    tier character varying(20) DEFAULT 'initia'::character varying,
    price numeric(8,2) DEFAULT 20.00,
    start_date timestamp with time zone DEFAULT now(),
    end_date timestamp with time zone,
    next_billing_date timestamp with time zone,
    trial_end_date timestamp with time zone,
    cancelled_date timestamp with time zone,
    created_date timestamp with time zone DEFAULT now(),
    last_payment_date timestamp with time zone,
    payment_method character varying(50) DEFAULT 'simulation'::character varying,
    CONSTRAINT chk_subscription_status CHECK (((status)::text = ANY ((ARRAY['trial'::character varying, 'active'::character varying, 'cancelled'::character varying, 'expired'::character varying])::text[]))),
    CONSTRAINT chk_subscription_tier CHECK (((tier)::text = ANY ((ARRAY['initia'::character varying, 'optima'::character varying, 'ultima'::character varying])::text[])))
);


--
-- Name: TABLE subscriptions; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.subscriptions IS 'Subscription management for different tiers';


--
-- Name: subscriptions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.subscriptions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: subscriptions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.subscriptions_id_seq OWNED BY public.subscriptions.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    id integer NOT NULL,
    email character varying(120) NOT NULL,
    password_hash character varying(255),
    first_name character varying(50) NOT NULL,
    last_name character varying(50) NOT NULL,
    phone character varying(20),
    profile_picture character varying(255),
    is_admin boolean DEFAULT false,
    is_active boolean DEFAULT true,
    date_created timestamp with time zone DEFAULT now(),
    last_login timestamp with time zone,
    user_type character varying(20) DEFAULT 'client'::character varying,
    is_prospect boolean DEFAULT false,
    prospect_source character varying(50),
    prospect_status character varying(20),
    prospect_notes text,
    appointment_requested boolean DEFAULT false,
    appointment_status character varying(20),
    assigned_to character varying(100),
    last_contact timestamp with time zone,
    invitation_token character varying(255),
    invitation_sent_at timestamp with time zone,
    invitation_expires_at timestamp with time zone,
    can_create_account boolean DEFAULT false,
    plan_selected boolean DEFAULT false NOT NULL,
    payment_completed boolean DEFAULT false NOT NULL,
    CONSTRAINT chk_user_type CHECK (((user_type)::text = ANY ((ARRAY['prospect'::character varying, 'client'::character varying])::text[])))
);


--
-- Name: TABLE users; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.users IS 'Main user table with prospect and client management';


--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: apprentissages id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.apprentissages ALTER COLUMN id SET DEFAULT nextval('public.apprentissages_id_seq'::regclass);


--
-- Name: credits id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.credits ALTER COLUMN id SET DEFAULT nextval('public.credits_id_seq'::regclass);


--
-- Name: crypto_prices id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.crypto_prices ALTER COLUMN id SET DEFAULT nextval('public.crypto_prices_id_seq'::regclass);


--
-- Name: investment_plan_lines id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.investment_plan_lines ALTER COLUMN id SET DEFAULT nextval('public.investment_plan_lines_id_seq'::regclass);


--
-- Name: investment_plans id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.investment_plans ALTER COLUMN id SET DEFAULT nextval('public.investment_plans_id_seq'::regclass);


--
-- Name: investor_profiles id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.investor_profiles ALTER COLUMN id SET DEFAULT nextval('public.investor_profiles_id_seq'::regclass);


--
-- Name: payment_methods id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payment_methods ALTER COLUMN id SET DEFAULT nextval('public.payment_methods_id_seq'::regclass);


--
-- Name: portfolio_holdings id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.portfolio_holdings ALTER COLUMN id SET DEFAULT nextval('public.portfolio_holdings_id_seq'::regclass);


--
-- Name: portfolios id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.portfolios ALTER COLUMN id SET DEFAULT nextval('public.portfolios_id_seq'::regclass);


--
-- Name: subscriptions id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.subscriptions ALTER COLUMN id SET DEFAULT nextval('public.subscriptions_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: apprentissages; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.apprentissages (id, nom, description, fichier_pdf, image, date_creation, date_modification, actif, ordre, fichier_pdf_original) FROM stdin;
5	Qu’est-ce qu’une assurance-vie ?	assurance vie, descriptio,	c838e0da635f4e549e577ba5d559f5f2.pdf	9f5cc0d5758e4405b80a46b41e780040.png	2025-11-28 12:08:40.278508	2025-11-28 12:15:52.470181	t	1	\N
\.


--
-- Data for Name: credits; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.credits (id, investor_profile_id, credit_type, description, initial_amount, remaining_amount, interest_rate, duration_years, monthly_payment, start_date, end_date, type_credit, montant_initial, montant_restant, taux_interet, duree_mois, mensualite, date_debut, date_fin, created_date, updated_date, calculated_monthly_payment, calculated_remaining_capital, last_calculation_date) FROM stdin;
\.


--
-- Data for Name: crypto_prices; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.crypto_prices (id, symbol, price_usd, price_eur, updated_at, created_at) FROM stdin;
108	bitcoin	87746.01	74671.85450999999	2025-12-23 11:31:19.119546	2025-12-17 15:48:02.309696
109	btc	87746.01	74671.85450999999	2025-12-23 11:31:19.119546	2025-12-17 15:48:02.807122
130	uniswap	5.858	4.985157999999999	2025-12-23 11:31:19.119546	2025-12-17 15:48:13.620177
131	uni	5.858	4.985157999999999	2025-12-23 11:31:19.119546	2025-12-17 15:48:14.1187
132	aave	151.41	128.84991	2025-12-23 11:31:19.119546	2025-12-17 15:48:14.614105
133	compound-governance-token	24.23	20.61973	2025-12-23 11:31:19.119546	2025-12-17 15:48:15.114605
134	comp	24.23	20.61973	2025-12-23 11:31:19.119546	2025-12-17 15:48:15.659253
135	maker	1813.7	1543.4587	2025-12-23 11:31:19.119546	2025-12-17 15:48:16.211605
136	mkr	1813.7	1543.4587	2025-12-23 11:31:19.119546	2025-12-17 15:48:16.758786
137	sushiswap	0.2919	0.24840689999999999	2025-12-23 11:31:19.119546	2025-12-17 15:48:17.248607
138	sushi	0.2919	0.24840689999999999	2025-12-23 11:31:19.119546	2025-12-17 15:48:17.814685
139	curve-dao-token	0.3691	0.3141041	2025-12-23 11:31:19.119546	2025-12-17 15:48:18.301267
140	crv	0.3691	0.3141041	2025-12-23 11:31:19.119546	2025-12-17 15:48:18.793756
141	1inch	0.1522	0.1295222	2025-12-23 11:31:19.119546	2025-12-17 15:48:19.297647
142	tether	1.0003	0.8512552999999999	2025-12-23 11:31:19.119546	2025-12-17 15:48:19.798194
143	usdt	1.0003	0.8512552999999999	2025-12-23 11:31:19.119546	2025-12-17 15:48:20.289238
144	usd-coin	1.0003	0.8512552999999999	2025-12-23 11:31:19.119546	2025-12-17 15:48:20.7805
145	usdc	1.0003	0.8512552999999999	2025-12-23 11:31:19.119546	2025-12-17 15:48:21.274705
146	binance-usd	1.0003	0.8512552999999999	2025-12-23 11:31:19.119546	2025-12-17 15:48:21.813674
147	busd	1.0003	0.8512552999999999	2025-12-23 11:31:19.119546	2025-12-17 15:48:22.313603
148	dai	0	0	2025-12-23 11:31:19.119546	2025-12-17 15:48:22.811756
149	terrausd	0	0	2025-12-23 11:31:19.119546	2025-12-17 15:48:23.300462
150	ust	0	0	2025-12-23 11:31:19.119546	2025-12-17 15:48:23.816136
151	axie-infinity	0.831	0.707181	2025-12-23 11:31:19.119546	2025-12-17 15:48:24.306273
187	filecoin	1.284	1.092684	2025-12-23 11:31:19.119546	2025-12-17 15:48:42.550119
188	fil	1.284	1.092684	2025-12-23 11:31:19.119546	2025-12-17 15:48:43.087653
189	internet-computer	2.988	2.542788	2025-12-23 11:31:19.119546	2025-12-17 15:48:43.57379
190	icp	2.988	2.542788	2025-12-23 11:31:19.119546	2025-12-17 15:48:44.092282
191	hedera-hashgraph	0.11253	0.09576303	2025-12-23 11:31:19.119546	2025-12-17 15:48:44.592664
192	hbar	0.11253	0.09576303	2025-12-23 11:31:19.119546	2025-12-17 15:48:45.07944
193	elrond-egd-2	6.23	5.30173	2025-12-23 11:31:19.119546	2025-12-17 15:48:45.567394
194	egld	6.23	5.30173	2025-12-23 11:31:19.119546	2025-12-17 15:48:46.103233
195	stellar	0.2178	0.18534779999999998	2025-12-23 11:31:19.119546	2025-12-17 15:48:46.612288
196	xlm	0.2178	0.18534779999999998	2025-12-23 11:31:19.119546	2025-12-17 15:48:47.148251
197	wrapped-bitcoin	87595.88	74544.09388	2025-12-23 11:31:19.119546	2025-12-17 15:48:47.645723
198	shiba-inu	7.16e-06	6.09316e-06	2025-12-23 11:31:19.119546	2025-12-17 15:48:48.188136
199	near	1.495	1.272245	2025-12-23 11:31:19.119546	2025-12-17 15:48:48.66706
200	aptos	1.604	1.365004	2025-12-23 11:31:19.119546	2025-12-17 15:48:49.165715
201	arbitrum	0.18599999999999997	0.15828599999999998	2025-12-23 11:31:19.119546	2025-12-17 15:48:49.659049
202	first-digital-usd	0.9993000000000001	0.8504043	2025-12-23 11:31:19.119546	2025-12-17 15:48:50.149799
203	optimism	0.2694	0.22925939999999997	2025-12-23 11:31:19.119546	2025-12-17 15:48:50.643328
204	immutable-x	0.22699999999999998	0.193177	2025-12-23 11:31:19.119546	2025-12-17 15:48:51.143596
205	render-token	7.029999999999999	5.98253	2025-12-23 11:31:19.119546	2025-12-17 15:48:51.653744
206	the-graph	0.03712	0.03158912	2025-12-23 11:31:19.119546	2025-12-17 15:48:52.212953
207	injective-protocol	4.596	3.911196	2025-12-23 11:31:19.119546	2025-12-17 15:48:52.704711
208	sei-network	0.1106	0.0941206	2025-12-23 11:31:19.119546	2025-12-17 15:48:53.275083
209	bittensor	217.3	184.9223	2025-12-23 11:31:19.119546	2025-12-17 15:48:53.8194
210	rune	0.57	0.48506999999999995	2025-12-23 11:31:19.119546	2025-12-17 15:48:54.410671
211	stacks	0.245	0.20849499999999999	2025-12-23 11:31:19.119546	2025-12-17 15:48:54.413248
110	ethereum	2970.22	2527.6572199999996	2025-12-23 11:31:19.119546	2025-12-17 15:48:03.346367
111	eth	2970.22	2527.6572199999996	2025-12-23 11:31:19.119546	2025-12-17 15:48:03.864812
112	binancecoin	852.5	725.4775	2025-12-23 11:31:19.119546	2025-12-17 15:48:04.363598
113	bnb	852.5	725.4775	2025-12-23 11:31:19.119546	2025-12-17 15:48:04.889446
114	ripple	1.9005	1.6173255	2025-12-23 11:31:19.119546	2025-12-17 15:48:05.384127
115	xrp	1.9005	1.6173255	2025-12-23 11:31:19.119546	2025-12-17 15:48:05.8805
117	sol	124.93	106.31543	2025-12-23 11:31:19.119546	2025-12-17 15:48:06.882241
152	axs	0.831	0.707181	2025-12-23 11:31:19.119546	2025-12-17 15:48:24.818183
153	the-sandbox	0.1136	0.0966736	2025-12-23 11:31:19.119546	2025-12-17 15:48:25.307267
154	sand	0.1136	0.0966736	2025-12-23 11:31:19.119546	2025-12-17 15:48:25.816582
155	decentraland	0.12149999999999998	0.10339649999999999	2025-12-23 11:31:19.119546	2025-12-17 15:48:26.30853
156	mana	0.12149999999999998	0.10339649999999999	2025-12-23 11:31:19.119546	2025-12-17 15:48:26.845484
157	enjincoin	0.0267	0.0227217	2025-12-23 11:31:19.119546	2025-12-17 15:48:27.339557
158	enj	0.0267	0.0227217	2025-12-23 11:31:19.119546	2025-12-17 15:48:27.871538
159	gala	0.006100000000000001	0.005191100000000001	2025-12-23 11:31:19.119546	2025-12-17 15:48:28.394795
160	flow	0.168	0.142968	2025-12-23 11:31:19.119546	2025-12-17 15:48:28.913305
161	litecoin	76.86	65.40786	2025-12-23 11:31:19.119546	2025-12-17 15:48:29.4093
162	ltc	76.86	65.40786	2025-12-23 11:31:19.119546	2025-12-17 15:48:29.931742
163	bitcoin-cash	581.3	494.68629999999996	2025-12-23 11:31:19.119546	2025-12-17 15:48:30.432895
164	bch	581.3	494.68629999999996	2025-12-23 11:31:19.119546	2025-12-17 15:48:30.926386
165	ethereum-classic	12.15	10.33965	2025-12-23 11:31:19.119546	2025-12-17 15:48:31.399717
166	etc	12.15	10.33965	2025-12-23 11:31:19.119546	2025-12-17 15:48:31.88682
167	monero	118.7	101.0137	2025-12-23 11:31:19.119546	2025-12-17 15:48:32.380265
168	xmr	118.7	101.0137	2025-12-23 11:31:19.119546	2025-12-17 15:48:32.867812
169	zcash	418.97	356.54347	2025-12-23 11:31:19.119546	2025-12-17 15:48:33.398936
170	zec	418.97	356.54347	2025-12-23 11:31:19.119546	2025-12-17 15:48:33.894085
171	dash	37.61	32.00611	2025-12-23 11:31:19.119546	2025-12-17 15:48:34.408111
172	neo	3.546	3.0176459999999996	2025-12-23 11:31:19.119546	2025-12-17 15:48:34.971632
173	iota	0.0835	0.0710585	2025-12-23 11:31:19.119546	2025-12-17 15:48:35.487912
174	miota	0.0835	0.0710585	2025-12-23 11:31:19.119546	2025-12-17 15:48:35.977887
175	polygon	0.37940000000000007	0.32286940000000003	2025-12-23 11:31:19.119546	2025-12-17 15:48:36.482326
176	matic	0.37940000000000007	0.32286940000000003	2025-12-23 11:31:19.119546	2025-12-17 15:48:36.97453
177	fantom	0.6994	0.5951894	2025-12-23 11:31:19.119546	2025-12-17 15:48:37.480606
178	ftm	0.6994	0.5951894	2025-12-23 11:31:19.119546	2025-12-17 15:48:37.971217
179	cosmos	1.956	1.664556	2025-12-23 11:31:19.119546	2025-12-17 15:48:38.48372
180	atom	1.956	1.664556	2025-12-23 11:31:19.119546	2025-12-17 15:48:38.98094
181	algorand	0.1103	0.0938653	2025-12-23 11:31:19.119546	2025-12-17 15:48:39.475066
182	algo	0.1103	0.0938653	2025-12-23 11:31:19.119546	2025-12-17 15:48:40.009866
183	vechain	0.01051	0.00894401	2025-12-23 11:31:19.119546	2025-12-17 15:48:40.507167
184	vet	0.01051	0.00894401	2025-12-23 11:31:19.119546	2025-12-17 15:48:41.031919
185	theta-token	0.275	0.234025	2025-12-23 11:31:19.119546	2025-12-17 15:48:41.526334
186	theta	0.275	0.234025	2025-12-23 11:31:19.119546	2025-12-17 15:48:42.060827
116	solana	124.93	106.31543	2025-12-23 11:31:19.119546	2025-12-17 15:48:06.38544
118	cardano	0.3679	0.3130829	2025-12-23 11:31:19.119546	2025-12-17 15:48:07.377506
119	ada	0.3679	0.3130829	2025-12-23 11:31:19.119546	2025-12-17 15:48:07.892344
120	avalanche-2	12.29	10.458789999999999	2025-12-23 11:31:19.119546	2025-12-17 15:48:08.459233
121	avax	12.29	10.458789999999999	2025-12-23 11:31:19.119546	2025-12-17 15:48:08.969544
122	dogecoin	0.13108	0.11154908	2025-12-23 11:31:19.119546	2025-12-17 15:48:09.460917
123	doge	0.13108	0.11154908	2025-12-23 11:31:19.119546	2025-12-17 15:48:09.957381
124	tron	0.2842	0.2418542	2025-12-23 11:31:19.119546	2025-12-17 15:48:10.448696
125	trx	0.2842	0.2418542	2025-12-23 11:31:19.119546	2025-12-17 15:48:10.94829
126	polkadot	1.776	1.511376	2025-12-23 11:31:19.119546	2025-12-17 15:48:11.464267
127	dot	1.776	1.511376	2025-12-23 11:31:19.119546	2025-12-17 15:48:12.008082
128	chainlink	12.38	10.53538	2025-12-23 11:31:19.119546	2025-12-17 15:48:12.544342
129	link	12.38	10.53538	2025-12-23 11:31:19.119546	2025-12-17 15:48:13.039378
\.


--
-- Data for Name: investment_plan_lines; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.investment_plan_lines (id, plan_id, support_envelope, description, reference, percentage, order_index, created_at, updated_at) FROM stdin;
7	1	PEA	ETF World	HD665HHGG	65	0	2025-12-20 14:53:17.465924	2025-12-20 14:53:17.465933
8	1	PER	SCPI	J87GGH65B5	35	1	2025-12-20 14:53:17.465934	2025-12-20 14:53:17.465934
\.


--
-- Data for Name: investment_plans; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.investment_plans (id, user_id, name, is_active, created_at, updated_at) FROM stdin;
1	2	Plan d'investissement principal	t	2025-12-20 14:12:27.178937	2025-12-20 14:12:27.178946
3	11	Mon plan d'investissement	t	2025-12-20 23:59:40.435941	2025-12-20 23:59:40.435948
4	12	Mon plan d'investissement	t	2025-12-21 00:02:06.683747	2025-12-21 00:02:06.683756
5	10	Mon plan d'investissement	t	2025-12-22 23:05:53.528445	2025-12-22 23:05:53.528455
6	13	Mon plan d'investissement	t	2025-12-22 23:20:28.73332	2025-12-22 23:20:28.733329
\.


--
-- Data for Name: investor_profiles; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.investor_profiles (id, user_id, monthly_net_income, monthly_savings_capacity, current_savings, impots_mensuels, risk_tolerance, investment_experience, investment_goals, investment_horizon, civilite, date_naissance, lieu_naissance, nationalite, pays_residence, pays_residence_fiscal, family_situation, professional_situation, metier, objectif_premiers_pas, objectif_constituer_capital, objectif_diversifier, objectif_optimiser_rendement, objectif_preparer_retraite, objectif_securite_financiere, objectif_projet_immobilier, objectif_revenus_complementaires, objectif_transmettre_capital, objectif_proteger_famille, tolerance_risque, horizon_placement, besoin_liquidite, experience_investissement, attitude_volatilite, has_livret_a, livret_a_value, has_ldds, ldds_value, has_lep, lep_value, has_pel_cel, pel_cel_value, has_current_account, current_account_value, liquidites_personnalisees_json, has_pea, pea_value, has_per, per_value, has_life_insurance, life_insurance_value, has_pee, pee_value, has_scpi, scpi_value, placements_personnalises_json, has_real_estate, real_estate_value, has_immobilier, immobilier_value, immobilier_data_json, has_autres_biens, autres_biens_value, autres_biens_data_json, cryptomonnaies_data_json, credits_data_json, revenus_complementaires, revenus_complementaires_json, charges_mensuelles, charges_mensuelles_json, has_pel, pel_value, has_cel, cel_value, has_autres_livrets, autres_livrets_value, has_cto, cto_value, has_private_equity, private_equity_value, has_crowdfunding, crowdfunding_value, other_investments, objectif_constitution_epargne, objectif_retraite, objectif_transmission, objectif_defiscalisation, objectif_immobilier, profil_risque_connu, profil_risque_choisi, question_1_reponse, question_2_reponse, question_3_reponse, question_4_reponse, question_5_reponse, synthese_profil_risque, cryptos_json, liquidites_personnalisees_json_legacy, placements_personnalises_json_legacy, date_completed, last_updated, professional_situation_other, calculated_total_liquidites, calculated_total_placements, calculated_total_immobilier_net, calculated_total_cryptomonnaies, calculated_total_autres_biens, calculated_total_credits_consommation, calculated_total_actifs, calculated_patrimoine_total_net, last_calculation_date) FROM stdin;
4	13	5000.00	1000.00	0.00	0.00	modéré	intermédiaire		long	M.	1998-12-13	KUALA LUMPUR	Française	France	\N	Célibataire	Salarié	Cadre Ingénieur	f	f	f	t	t	t	f	f	f	f	15	long	non	intermédiaire	attendre	t	2000.00	f	0.00	f	0.00	f	0.00	f	0.00	\N	t	15000.00	f	0.00	f	0.00	f	0.00	f	0.00	\N	t	230000.00	t	230000.00	[{"type": "residence_principale", "valeur": 230000.0, "surface": 45.0, "has_credit": true, "credit_date": "2025-09", "credit_taeg": 3.5, "description": "Appartement asnieres sur seine", "credit_duree": 25, "credit_montant": 200000.0, "calculated_valeur_nette": 34005.0}]	f	0.00	[{"name": "Hugues Marie", "valeur": 1000.0}]	[{"symbol": "binancecoin", "quantity": 1.0, "last_updated": "2025-12-22T23:35:57.750433", "current_price": 733.2017, "calculated_value": 733.2017}]	[]	0.00	\N	0.00	\N	f	0.00	f	0.00	f	0.00	f	0.00	f	0.00	f	0.00	\N	f	f	f	f	f	f	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-22 23:15:44.149787+01	2025-12-23 00:35:57.742209+01	cadre	2000	15000	34005	733.2	1000	0	52738.2	52738.2	2025-12-22 23:35:57.750519
1	2	4000.00	1000.00	0.00	0.00	modéré	débutant		court	M.	1998-12-13	KUALA LUMPUR	Française	France	\N	Célibataire	Salarié	Cadre Ingénieur	t	t	t	f	f	f	t	t	f	f	5	court	oui	débutant	investir_plus	t	4700.00	f	0.00	f	0.00	f	0.00	f	0.00	null	t	23000.00	f	0.00	f	0.00	f	0.00	f	0.00	null	t	250000.00	t	250000.00	[{"type": "investissement_locatif", "valeur": 250000.0, "surface": 43.0, "has_credit": true, "credit_date": "2025-10", "credit_taeg": 3.35, "description": "Appartement asnieres sur seine", "credit_duree": 25, "credit_montant": 215000.0, "calculated_valeur_nette": 38177.0}]	f	0.00	[{"name": "Voiture", "valeur": 4000.0}, {"name": "Scooter", "valeur": 4000.0}]	[{"symbol": "bitcoin", "quantity": 0.1, "last_updated": "2025-12-23T11:07:44.998978", "current_price": 74595.40067, "calculated_value": 7459.540067}, {"symbol": "binancecoin", "quantity": 1.5, "last_updated": "2025-12-23T11:07:44.998997", "current_price": 724.70309, "calculated_value": 1087.054635}, {"symbol": "ethereum", "quantity": 0.5, "last_updated": "2025-12-23T11:07:44.999007", "current_price": 2524.78084, "calculated_value": 1262.39042}, {"symbol": "solana", "quantity": 10.0, "last_updated": "2025-12-23T11:07:44.999016", "current_price": 106.33245, "calculated_value": 1063.3245}]	[{"id": "", "taux": 6.5, "duree": 5, "mensualite": 97.83, "date_depart": "2025-01", "description": "Crédit auto", "montant_initial": 5000.0, "montant_restant": 3826.03}]	1400.00	[{"name": "Loyers immobiliers", "amount": 1350.0}, {"name": "Dividendes", "amount": 50.0}]	226.00	[{"name": "parking auto", "amount": 126.0}, {"name": "Assurances", "amount": 100.0}]	f	0.00	f	0.00	f	0.00	t	2500.00	f	0.00	f	0.00	\N	f	f	f	f	f	f	\N	\N	\N	\N	\N	\N	\N	[{"symbol": "BTC", "quantity": 0.25}, {"symbol": "ETH", "quantity": 3.0}]	\N	\N	2025-10-05 13:09:41.395387+02	2025-12-23 12:07:44.990765+01	\N	4700	25500	38177.36	10872.31	8000	3826.03	87249.67	83423.64	2025-12-23 11:07:44.99911
3	10	0.00	0.00	0.00	0.00	modere	debutant		long terme	\N	\N	\N	\N	\N	\N	Célibataire	Salarié	\N	f	f	f	f	f	f	f	f	f	f	\N	\N	\N	\N	\N	f	0.00	f	0.00	f	0.00	f	0.00	f	0.00	\N	f	0.00	f	0.00	f	0.00	f	0.00	f	0.00	\N	f	0.00	f	0.00	\N	f	0.00	\N	\N	\N	\N	\N	\N	\N	f	0.00	f	0.00	f	0.00	f	0.00	f	0.00	f	0.00	\N	f	f	f	f	f	f	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-22 23:05:17.777341+01	2025-12-23 00:13:57.926811+01	\N	0	0	0	0	0	0	0	0	2025-12-22 23:13:57.93143
\.


--
-- Data for Name: payment_methods; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.payment_methods (id, user_id, method_type, provider, provider_id, is_default, is_active, created_date) FROM stdin;
\.


--
-- Data for Name: portfolio_holdings; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.portfolio_holdings (id, portfolio_id, asset_type, symbol, quantity, purchase_price, current_price, purchase_date, last_updated) FROM stdin;
\.


--
-- Data for Name: portfolios; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.portfolios (id, user_id, name, strategy, total_value, created_date, last_updated, cash_amount, invested_amount, monthly_contribution, target_allocation) FROM stdin;
\.


--
-- Data for Name: subscriptions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.subscriptions (id, user_id, status, tier, price, start_date, end_date, next_billing_date, trial_end_date, cancelled_date, created_date, last_payment_date, payment_method) FROM stdin;
1	2	active	optima	20.00	2025-11-14 13:09:41.39476+01	\N	2025-12-14 13:09:41.394764+01	\N	\N	2025-11-14 13:09:41.39521+01	2025-11-14 13:09:41.394768+01	simulation
11	10	active	initia	20.00	2025-12-22 23:05:17.744966+01	\N	2026-01-21 23:05:17.744968+01	\N	\N	2025-12-22 23:05:17.749056+01	2025-12-22 23:05:17.744972+01	card_simulation
12	13	active	initia	20.00	2025-12-22 23:15:44.1366+01	\N	2026-01-21 23:15:44.136602+01	\N	\N	2025-12-22 23:15:44.138227+01	2025-12-22 23:15:44.136604+01	card_simulation
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.users (id, email, password_hash, first_name, last_name, phone, profile_picture, is_admin, is_active, date_created, last_login, user_type, is_prospect, prospect_source, prospect_status, prospect_notes, appointment_requested, appointment_status, assigned_to, last_contact, invitation_token, invitation_sent_at, invitation_expires_at, can_create_account, plan_selected, payment_completed) FROM stdin;
13	dimitri@yopmail.com	pbkdf2:sha256:600000$bwCdQ4lr4AkX7zJP$049c7e528bda7414ad438bf6608071340d569b873f524feb582760747741f24a	dimitri	dimitri	0659986846	\N	f	t	2025-12-21 00:08:33.294975+01	2025-12-22 23:15:23.097035+01	client	f	site_vitrine	converti	\N	t	en_attente	\N	\N	\N	2025-12-21 00:08:55.664374+01	\N	f	t	t
11	test@yopmail.com	pbkdf2:sha256:600000$qqCeegmrDEWbBQ8Y$efff9519245b55929bbb7ed67abc144ba29bc24b7a7a05d30960e5c547118931	test	test	0659986846	\N	f	t	2025-12-20 23:24:33.309854+01	2025-12-20 23:32:19.941248+01	prospect	t	site_vitrine	contacté	\N	t	en_attente	\N	\N	\N	2025-12-20 23:25:22.192517+01	\N	f	f	f
6	prospect.test@gmail.com	pbkdf2:sha256:1000000$EBOjl7uIoj1ejKUM$dd7a1511038d82fd62dc66f537a1abba1a184d514f2646a39cd382d11b71a1bb	Test	Prospect	0612345678	\N	f	t	2025-12-20 22:50:50.519377+01	\N	prospect	t	manual_test	nouveau	\N	f	en_attente	\N	\N	\N	\N	\N	f	f	f
7	john@yopmail.com	pbkdf2:sha256:600000$L2IIuOeO0nzGCuLB$cca60af39b63e688ca1eede390037cc56eb04793d90022c02eeb9b027d72ee21	john	doe	dz	\N	f	t	2025-12-20 22:52:15.288934+01	\N	prospect	t	site_vitrine	nouveau	\N	t	en_attente	\N	\N	\N	\N	\N	f	f	f
8	titi@yopmail.com	pbkdf2:sha256:600000$Ty624FjTintONPSY$e51bddf98a2625cba580e7a830f30c1ed7c24a3f81bd31d01b0e0dbb1814cb4f	titi	tiit	8778	\N	f	t	2025-12-20 22:56:14.791328+01	\N	prospect	t	site_vitrine	nouveau	\N	t	en_attente	\N	\N	\N	\N	\N	f	f	f
12	rick@yopmail.com	pbkdf2:sha256:600000$1TxaRgZssZV86twp$0199d7f589a27a1edee469c917d240e27cfc1039361d1218895b61bdd45b418c	rick	rick	0659986846	\N	f	t	2025-12-21 00:00:50.521514+01	2025-12-21 00:01:59.843873+01	prospect	t	site_vitrine	contacté	\N	t	en_attente	\N	\N	\N	2025-12-21 00:01:15.44842+01	\N	f	f	f
1	admin@gmail.com	scrypt:32768:8:1$AM8zxmOx1aAq6sNz$9dd7213b84b407e7ed1013449add9cd10e6e882912e5b13b8c36a475ebb0841d586bac1d9b9e22d26ff4d6c577940a689376b0030e0d604c58b095635fa77867	Admin	Système	\N	\N	t	t	2025-11-12 20:47:26.769589+01	2025-12-23 13:40:04.589838+01	client	f	\N	nouveau	\N	f	en_attente	\N	\N	\N	\N	\N	f	f	f
2	test.client@gmail.com	pbkdf2:sha256:600000$lL0ln4vnCMKTUKZm$9a355ae4b728bf2c1931687ec300db69b94bf0ee5f4e0c1892c8f30c62489d2c	Hugues	MARIE	0659986846	\N	f	t	2025-09-30 13:09:41.246738+02	2025-12-23 13:46:31.557393+01	client	f	\N	nouveau	\N	f	en_attente	\N	\N	\N	\N	\N	f	f	f
10	ale@yopmail.com	pbkdf2:sha256:600000$OdnuALdKp7JPsUcp$368666e6cba1596e7c0e48560bf3679ad371330bcb4a9fd86e9688bbfcca9783	Alex	Test	0612345678	\N	f	t	2025-12-20 23:07:23.543078+01	2025-12-20 23:22:46.333008+01	client	f	site_vitrine	converti	\N	f	en_attente	\N	\N	\N	2025-12-20 23:09:42.887976+01	\N	f	t	t
\.


--
-- Name: apprentissages_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.apprentissages_id_seq', 5, true);


--
-- Name: credits_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.credits_id_seq', 1, false);


--
-- Name: crypto_prices_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.crypto_prices_id_seq', 211, true);


--
-- Name: investment_plan_lines_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.investment_plan_lines_id_seq', 8, true);


--
-- Name: investment_plans_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.investment_plans_id_seq', 6, true);


--
-- Name: investor_profiles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.investor_profiles_id_seq', 4, true);


--
-- Name: payment_methods_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.payment_methods_id_seq', 1, false);


--
-- Name: portfolio_holdings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.portfolio_holdings_id_seq', 1, false);


--
-- Name: portfolios_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.portfolios_id_seq', 1, false);


--
-- Name: subscriptions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.subscriptions_id_seq', 12, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.users_id_seq', 13, true);


--
-- Name: apprentissages apprentissages_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.apprentissages
    ADD CONSTRAINT apprentissages_pkey PRIMARY KEY (id);


--
-- Name: credits credits_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.credits
    ADD CONSTRAINT credits_pkey PRIMARY KEY (id);


--
-- Name: crypto_prices crypto_prices_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.crypto_prices
    ADD CONSTRAINT crypto_prices_pkey PRIMARY KEY (id);


--
-- Name: investment_plan_lines investment_plan_lines_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.investment_plan_lines
    ADD CONSTRAINT investment_plan_lines_pkey PRIMARY KEY (id);


--
-- Name: investment_plans investment_plans_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.investment_plans
    ADD CONSTRAINT investment_plans_pkey PRIMARY KEY (id);


--
-- Name: investor_profiles investor_profiles_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.investor_profiles
    ADD CONSTRAINT investor_profiles_pkey PRIMARY KEY (id);


--
-- Name: payment_methods payment_methods_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payment_methods
    ADD CONSTRAINT payment_methods_pkey PRIMARY KEY (id);


--
-- Name: portfolio_holdings portfolio_holdings_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.portfolio_holdings
    ADD CONSTRAINT portfolio_holdings_pkey PRIMARY KEY (id);


--
-- Name: portfolios portfolios_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.portfolios
    ADD CONSTRAINT portfolios_pkey PRIMARY KEY (id);


--
-- Name: subscriptions subscriptions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.subscriptions
    ADD CONSTRAINT subscriptions_pkey PRIMARY KEY (id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_invitation_token_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_invitation_token_key UNIQUE (invitation_token);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: idx_credits_profile; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_credits_profile ON public.credits USING btree (investor_profile_id);


--
-- Name: idx_investment_plans_user_active; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_investment_plans_user_active ON public.investment_plans USING btree (user_id, is_active);


--
-- Name: idx_investor_charges_jsonb; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_investor_charges_jsonb ON public.investor_profiles USING gin (charges_mensuelles_json);


--
-- Name: idx_investor_crypto_jsonb; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_investor_crypto_jsonb ON public.investor_profiles USING gin (cryptomonnaies_data_json);


--
-- Name: idx_investor_immobilier_jsonb; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_investor_immobilier_jsonb ON public.investor_profiles USING gin (immobilier_data_json);


--
-- Name: idx_investor_liquidites_jsonb; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_investor_liquidites_jsonb ON public.investor_profiles USING gin (liquidites_personnalisees_json);


--
-- Name: idx_investor_placements_jsonb; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_investor_placements_jsonb ON public.investor_profiles USING gin (placements_personnalises_json);


--
-- Name: idx_investor_profiles_risk; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_investor_profiles_risk ON public.investor_profiles USING btree (risk_tolerance);


--
-- Name: idx_investor_profiles_user; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_investor_profiles_user ON public.investor_profiles USING btree (user_id);


--
-- Name: idx_investor_revenus_jsonb; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_investor_revenus_jsonb ON public.investor_profiles USING gin (revenus_complementaires_json);


--
-- Name: idx_payment_methods_user; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_payment_methods_user ON public.payment_methods USING btree (user_id);


--
-- Name: idx_plan_lines_plan_order; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_plan_lines_plan_order ON public.investment_plan_lines USING btree (plan_id, order_index);


--
-- Name: idx_plan_order; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_plan_order ON public.investment_plan_lines USING btree (plan_id, order_index);


--
-- Name: idx_portfolio_holdings_portfolio; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_portfolio_holdings_portfolio ON public.portfolio_holdings USING btree (portfolio_id);


--
-- Name: idx_portfolios_user; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_portfolios_user ON public.portfolios USING btree (user_id);


--
-- Name: idx_subscriptions_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_subscriptions_status ON public.subscriptions USING btree (status, tier);


--
-- Name: idx_subscriptions_user; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_subscriptions_user ON public.subscriptions USING btree (user_id);


--
-- Name: idx_users_email; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_users_email ON public.users USING btree (email);


--
-- Name: idx_users_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_users_type ON public.users USING btree (user_type, is_prospect);


--
-- Name: ix_crypto_prices_symbol; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_crypto_prices_symbol ON public.crypto_prices USING btree (symbol);


--
-- Name: investment_plan_lines trigger_investment_plan_lines_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trigger_investment_plan_lines_updated_at BEFORE UPDATE ON public.investment_plan_lines FOR EACH ROW EXECUTE FUNCTION public.update_investment_plan_updated_at();


--
-- Name: investment_plans trigger_investment_plans_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trigger_investment_plans_updated_at BEFORE UPDATE ON public.investment_plans FOR EACH ROW EXECUTE FUNCTION public.update_investment_plan_updated_at();


--
-- Name: investor_profiles update_investor_profiles_last_updated; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_investor_profiles_last_updated BEFORE UPDATE ON public.investor_profiles FOR EACH ROW EXECUTE FUNCTION public.update_last_updated_column();


--
-- Name: portfolios update_portfolios_last_updated; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_portfolios_last_updated BEFORE UPDATE ON public.portfolios FOR EACH ROW EXECUTE FUNCTION public.update_last_updated_column();


--
-- Name: credits credits_investor_profile_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.credits
    ADD CONSTRAINT credits_investor_profile_id_fkey FOREIGN KEY (investor_profile_id) REFERENCES public.investor_profiles(id) ON DELETE CASCADE;


--
-- Name: investment_plan_lines investment_plan_lines_plan_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.investment_plan_lines
    ADD CONSTRAINT investment_plan_lines_plan_id_fkey FOREIGN KEY (plan_id) REFERENCES public.investment_plans(id);


--
-- Name: investment_plans investment_plans_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.investment_plans
    ADD CONSTRAINT investment_plans_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: investor_profiles investor_profiles_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.investor_profiles
    ADD CONSTRAINT investor_profiles_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: payment_methods payment_methods_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payment_methods
    ADD CONSTRAINT payment_methods_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: portfolio_holdings portfolio_holdings_portfolio_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.portfolio_holdings
    ADD CONSTRAINT portfolio_holdings_portfolio_id_fkey FOREIGN KEY (portfolio_id) REFERENCES public.portfolios(id) ON DELETE CASCADE;


--
-- Name: portfolios portfolios_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.portfolios
    ADD CONSTRAINT portfolios_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: subscriptions subscriptions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.subscriptions
    ADD CONSTRAINT subscriptions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict a67JRawDB9CxGZtw0VEJduZkmwbyvvwrHACgXznqqQ0pNlJWju5uwFgIZba0bhJ

