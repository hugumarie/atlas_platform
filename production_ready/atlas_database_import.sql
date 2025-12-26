--
-- PostgreSQL database dump
--

\restrict 3JqG1GcefMVzNQBSnbw8YqzzTiLIBbvOnN8QZKEHXZVW65vrUjfJ8WzJbc9KJMA

-- Dumped from database version 16.11 (Homebrew)
-- Dumped by pg_dump version 16.11 (Homebrew)

-- Started on 2025-12-23 11:08:07 CET

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

DROP DATABASE IF EXISTS atlas_db;
--
-- TOC entry 3965 (class 1262 OID 16384)
-- Name: atlas_db; Type: DATABASE; Schema: -; Owner: huguesmarie
--

CREATE DATABASE atlas_db WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'en_US.UTF-8';


ALTER DATABASE atlas_db OWNER TO huguesmarie;

\unrestrict 3JqG1GcefMVzNQBSnbw8YqzzTiLIBbvOnN8QZKEHXZVW65vrUjfJ8WzJbc9KJMA
\connect atlas_db
\restrict 3JqG1GcefMVzNQBSnbw8YqzzTiLIBbvOnN8QZKEHXZVW65vrUjfJ8WzJbc9KJMA

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
-- TOC entry 238 (class 1255 OID 16738)
-- Name: update_investment_plan_updated_at(); Type: FUNCTION; Schema: public; Owner: huguesmarie
--

CREATE FUNCTION public.update_investment_plan_updated_at() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_investment_plan_updated_at() OWNER TO huguesmarie;

--
-- TOC entry 237 (class 1255 OID 16584)
-- Name: update_last_updated_column(); Type: FUNCTION; Schema: public; Owner: huguesmarie
--

CREATE FUNCTION public.update_last_updated_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.last_updated = NOW();
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_last_updated_column() OWNER TO huguesmarie;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 230 (class 1259 OID 16691)
-- Name: apprentissages; Type: TABLE; Schema: public; Owner: huguesmarie
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


ALTER TABLE public.apprentissages OWNER TO huguesmarie;

--
-- TOC entry 229 (class 1259 OID 16690)
-- Name: apprentissages_id_seq; Type: SEQUENCE; Schema: public; Owner: huguesmarie
--

CREATE SEQUENCE public.apprentissages_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.apprentissages_id_seq OWNER TO huguesmarie;

--
-- TOC entry 3966 (class 0 OID 0)
-- Dependencies: 229
-- Name: apprentissages_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: huguesmarie
--

ALTER SEQUENCE public.apprentissages_id_seq OWNED BY public.apprentissages.id;


--
-- TOC entry 226 (class 1259 OID 16549)
-- Name: credits; Type: TABLE; Schema: public; Owner: huguesmarie
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


ALTER TABLE public.credits OWNER TO huguesmarie;

--
-- TOC entry 3967 (class 0 OID 0)
-- Dependencies: 226
-- Name: TABLE credits; Type: COMMENT; Schema: public; Owner: huguesmarie
--

COMMENT ON TABLE public.credits IS 'Detailed credit tracking';


--
-- TOC entry 3968 (class 0 OID 0)
-- Dependencies: 226
-- Name: COLUMN credits.calculated_remaining_capital; Type: COMMENT; Schema: public; Owner: huguesmarie
--

COMMENT ON COLUMN public.credits.calculated_remaining_capital IS 'Capital restant calculé automatiquement selon amortissement';


--
-- TOC entry 3969 (class 0 OID 0)
-- Dependencies: 226
-- Name: COLUMN credits.last_calculation_date; Type: COMMENT; Schema: public; Owner: huguesmarie
--

COMMENT ON COLUMN public.credits.last_calculation_date IS 'Date du dernier calcul automatique';


--
-- TOC entry 225 (class 1259 OID 16548)
-- Name: credits_id_seq; Type: SEQUENCE; Schema: public; Owner: huguesmarie
--

CREATE SEQUENCE public.credits_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.credits_id_seq OWNER TO huguesmarie;

--
-- TOC entry 3970 (class 0 OID 0)
-- Dependencies: 225
-- Name: credits_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: huguesmarie
--

ALTER SEQUENCE public.credits_id_seq OWNED BY public.credits.id;


--
-- TOC entry 232 (class 1259 OID 16700)
-- Name: crypto_prices; Type: TABLE; Schema: public; Owner: huguesmarie
--

CREATE TABLE public.crypto_prices (
    id integer NOT NULL,
    symbol character varying(50) NOT NULL,
    price_usd double precision NOT NULL,
    price_eur double precision NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE public.crypto_prices OWNER TO huguesmarie;

--
-- TOC entry 231 (class 1259 OID 16699)
-- Name: crypto_prices_id_seq; Type: SEQUENCE; Schema: public; Owner: huguesmarie
--

CREATE SEQUENCE public.crypto_prices_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.crypto_prices_id_seq OWNER TO huguesmarie;

--
-- TOC entry 3971 (class 0 OID 0)
-- Dependencies: 231
-- Name: crypto_prices_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: huguesmarie
--

ALTER SEQUENCE public.crypto_prices_id_seq OWNED BY public.crypto_prices.id;


--
-- TOC entry 236 (class 1259 OID 16721)
-- Name: investment_plan_lines; Type: TABLE; Schema: public; Owner: huguesmarie
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


ALTER TABLE public.investment_plan_lines OWNER TO huguesmarie;

--
-- TOC entry 3972 (class 0 OID 0)
-- Dependencies: 236
-- Name: TABLE investment_plan_lines; Type: COMMENT; Schema: public; Owner: huguesmarie
--

COMMENT ON TABLE public.investment_plan_lines IS 'Lignes de détail des plans d investissement';


--
-- TOC entry 3973 (class 0 OID 0)
-- Dependencies: 236
-- Name: COLUMN investment_plan_lines.support_envelope; Type: COMMENT; Schema: public; Owner: huguesmarie
--

COMMENT ON COLUMN public.investment_plan_lines.support_envelope IS 'Type d enveloppe (PEA, Assurance Vie, etc.)';


--
-- TOC entry 3974 (class 0 OID 0)
-- Dependencies: 236
-- Name: COLUMN investment_plan_lines.description; Type: COMMENT; Schema: public; Owner: huguesmarie
--

COMMENT ON COLUMN public.investment_plan_lines.description IS 'Description du placement (ex: ETF World)';


--
-- TOC entry 3975 (class 0 OID 0)
-- Dependencies: 236
-- Name: COLUMN investment_plan_lines.reference; Type: COMMENT; Schema: public; Owner: huguesmarie
--

COMMENT ON COLUMN public.investment_plan_lines.reference IS 'Référence du placement (ex: ISIN)';


--
-- TOC entry 3976 (class 0 OID 0)
-- Dependencies: 236
-- Name: COLUMN investment_plan_lines.percentage; Type: COMMENT; Schema: public; Owner: huguesmarie
--

COMMENT ON COLUMN public.investment_plan_lines.percentage IS 'Pourcentage du montant mensuel à investir';


--
-- TOC entry 3977 (class 0 OID 0)
-- Dependencies: 236
-- Name: COLUMN investment_plan_lines.order_index; Type: COMMENT; Schema: public; Owner: huguesmarie
--

COMMENT ON COLUMN public.investment_plan_lines.order_index IS 'Ordre d affichage des lignes';


--
-- TOC entry 235 (class 1259 OID 16720)
-- Name: investment_plan_lines_id_seq; Type: SEQUENCE; Schema: public; Owner: huguesmarie
--

CREATE SEQUENCE public.investment_plan_lines_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.investment_plan_lines_id_seq OWNER TO huguesmarie;

--
-- TOC entry 3978 (class 0 OID 0)
-- Dependencies: 235
-- Name: investment_plan_lines_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: huguesmarie
--

ALTER SEQUENCE public.investment_plan_lines_id_seq OWNED BY public.investment_plan_lines.id;


--
-- TOC entry 234 (class 1259 OID 16709)
-- Name: investment_plans; Type: TABLE; Schema: public; Owner: huguesmarie
--

CREATE TABLE public.investment_plans (
    id integer NOT NULL,
    user_id integer NOT NULL,
    name character varying(100) NOT NULL,
    is_active boolean NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


ALTER TABLE public.investment_plans OWNER TO huguesmarie;

--
-- TOC entry 3979 (class 0 OID 0)
-- Dependencies: 234
-- Name: TABLE investment_plans; Type: COMMENT; Schema: public; Owner: huguesmarie
--

COMMENT ON TABLE public.investment_plans IS 'Plans d investissement mensuel des utilisateurs';


--
-- TOC entry 3980 (class 0 OID 0)
-- Dependencies: 234
-- Name: COLUMN investment_plans.user_id; Type: COMMENT; Schema: public; Owner: huguesmarie
--

COMMENT ON COLUMN public.investment_plans.user_id IS 'ID de l utilisateur propriétaire du plan';


--
-- TOC entry 3981 (class 0 OID 0)
-- Dependencies: 234
-- Name: COLUMN investment_plans.name; Type: COMMENT; Schema: public; Owner: huguesmarie
--

COMMENT ON COLUMN public.investment_plans.name IS 'Nom du plan (par défaut: Plan principal)';


--
-- TOC entry 3982 (class 0 OID 0)
-- Dependencies: 234
-- Name: COLUMN investment_plans.is_active; Type: COMMENT; Schema: public; Owner: huguesmarie
--

COMMENT ON COLUMN public.investment_plans.is_active IS 'Indique si le plan est actif';


--
-- TOC entry 233 (class 1259 OID 16708)
-- Name: investment_plans_id_seq; Type: SEQUENCE; Schema: public; Owner: huguesmarie
--

CREATE SEQUENCE public.investment_plans_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.investment_plans_id_seq OWNER TO huguesmarie;

--
-- TOC entry 3983 (class 0 OID 0)
-- Dependencies: 233
-- Name: investment_plans_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: huguesmarie
--

ALTER SEQUENCE public.investment_plans_id_seq OWNED BY public.investment_plans.id;


--
-- TOC entry 218 (class 1259 OID 16412)
-- Name: investor_profiles; Type: TABLE; Schema: public; Owner: huguesmarie
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


ALTER TABLE public.investor_profiles OWNER TO huguesmarie;

--
-- TOC entry 3984 (class 0 OID 0)
-- Dependencies: 218
-- Name: TABLE investor_profiles; Type: COMMENT; Schema: public; Owner: huguesmarie
--

COMMENT ON TABLE public.investor_profiles IS 'Detailed financial profiles with JSONB fields for complex data';


--
-- TOC entry 3985 (class 0 OID 0)
-- Dependencies: 218
-- Name: COLUMN investor_profiles.calculated_total_liquidites; Type: COMMENT; Schema: public; Owner: huguesmarie
--

COMMENT ON COLUMN public.investor_profiles.calculated_total_liquidites IS 'Total des liquidités calculé et sauvegardé';


--
-- TOC entry 3986 (class 0 OID 0)
-- Dependencies: 218
-- Name: COLUMN investor_profiles.calculated_total_placements; Type: COMMENT; Schema: public; Owner: huguesmarie
--

COMMENT ON COLUMN public.investor_profiles.calculated_total_placements IS 'Total des placements financiers calculé et sauvegardé';


--
-- TOC entry 3987 (class 0 OID 0)
-- Dependencies: 218
-- Name: COLUMN investor_profiles.calculated_total_immobilier_net; Type: COMMENT; Schema: public; Owner: huguesmarie
--

COMMENT ON COLUMN public.investor_profiles.calculated_total_immobilier_net IS 'Total immobilier net (valeur - crédits immobiliers) calculé et sauvegardé';


--
-- TOC entry 3988 (class 0 OID 0)
-- Dependencies: 218
-- Name: COLUMN investor_profiles.calculated_total_cryptomonnaies; Type: COMMENT; Schema: public; Owner: huguesmarie
--

COMMENT ON COLUMN public.investor_profiles.calculated_total_cryptomonnaies IS 'Total des cryptomonnaies avec prix actuels calculé et sauvegardé';


--
-- TOC entry 3989 (class 0 OID 0)
-- Dependencies: 218
-- Name: COLUMN investor_profiles.calculated_total_autres_biens; Type: COMMENT; Schema: public; Owner: huguesmarie
--

COMMENT ON COLUMN public.investor_profiles.calculated_total_autres_biens IS 'Total des autres biens calculé et sauvegardé';


--
-- TOC entry 3990 (class 0 OID 0)
-- Dependencies: 218
-- Name: COLUMN investor_profiles.calculated_total_credits_consommation; Type: COMMENT; Schema: public; Owner: huguesmarie
--

COMMENT ON COLUMN public.investor_profiles.calculated_total_credits_consommation IS 'Total des crédits de consommation restants calculé et sauvegardé';


--
-- TOC entry 3991 (class 0 OID 0)
-- Dependencies: 218
-- Name: COLUMN investor_profiles.calculated_total_actifs; Type: COMMENT; Schema: public; Owner: huguesmarie
--

COMMENT ON COLUMN public.investor_profiles.calculated_total_actifs IS 'Total de tous les actifs calculé et sauvegardé';


--
-- TOC entry 3992 (class 0 OID 0)
-- Dependencies: 218
-- Name: COLUMN investor_profiles.calculated_patrimoine_total_net; Type: COMMENT; Schema: public; Owner: huguesmarie
--

COMMENT ON COLUMN public.investor_profiles.calculated_patrimoine_total_net IS 'Patrimoine total net (actifs - crédits) calculé et sauvegardé';


--
-- TOC entry 3993 (class 0 OID 0)
-- Dependencies: 218
-- Name: COLUMN investor_profiles.last_calculation_date; Type: COMMENT; Schema: public; Owner: huguesmarie
--

COMMENT ON COLUMN public.investor_profiles.last_calculation_date IS 'Date de dernière mise à jour des calculs patrimoniaux';


--
-- TOC entry 217 (class 1259 OID 16411)
-- Name: investor_profiles_id_seq; Type: SEQUENCE; Schema: public; Owner: huguesmarie
--

CREATE SEQUENCE public.investor_profiles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.investor_profiles_id_seq OWNER TO huguesmarie;

--
-- TOC entry 3994 (class 0 OID 0)
-- Dependencies: 217
-- Name: investor_profiles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: huguesmarie
--

ALTER SEQUENCE public.investor_profiles_id_seq OWNED BY public.investor_profiles.id;


--
-- TOC entry 228 (class 1259 OID 16564)
-- Name: payment_methods; Type: TABLE; Schema: public; Owner: huguesmarie
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


ALTER TABLE public.payment_methods OWNER TO huguesmarie;

--
-- TOC entry 3995 (class 0 OID 0)
-- Dependencies: 228
-- Name: TABLE payment_methods; Type: COMMENT; Schema: public; Owner: huguesmarie
--

COMMENT ON TABLE public.payment_methods IS 'User payment method management';


--
-- TOC entry 227 (class 1259 OID 16563)
-- Name: payment_methods_id_seq; Type: SEQUENCE; Schema: public; Owner: huguesmarie
--

CREATE SEQUENCE public.payment_methods_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.payment_methods_id_seq OWNER TO huguesmarie;

--
-- TOC entry 3996 (class 0 OID 0)
-- Dependencies: 227
-- Name: payment_methods_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: huguesmarie
--

ALTER SEQUENCE public.payment_methods_id_seq OWNED BY public.payment_methods.id;


--
-- TOC entry 224 (class 1259 OID 16534)
-- Name: portfolio_holdings; Type: TABLE; Schema: public; Owner: huguesmarie
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


ALTER TABLE public.portfolio_holdings OWNER TO huguesmarie;

--
-- TOC entry 223 (class 1259 OID 16533)
-- Name: portfolio_holdings_id_seq; Type: SEQUENCE; Schema: public; Owner: huguesmarie
--

CREATE SEQUENCE public.portfolio_holdings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.portfolio_holdings_id_seq OWNER TO huguesmarie;

--
-- TOC entry 3997 (class 0 OID 0)
-- Dependencies: 223
-- Name: portfolio_holdings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: huguesmarie
--

ALTER SEQUENCE public.portfolio_holdings_id_seq OWNED BY public.portfolio_holdings.id;


--
-- TOC entry 222 (class 1259 OID 16519)
-- Name: portfolios; Type: TABLE; Schema: public; Owner: huguesmarie
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


ALTER TABLE public.portfolios OWNER TO huguesmarie;

--
-- TOC entry 3998 (class 0 OID 0)
-- Dependencies: 222
-- Name: TABLE portfolios; Type: COMMENT; Schema: public; Owner: huguesmarie
--

COMMENT ON TABLE public.portfolios IS 'Investment portfolios for users';


--
-- TOC entry 221 (class 1259 OID 16518)
-- Name: portfolios_id_seq; Type: SEQUENCE; Schema: public; Owner: huguesmarie
--

CREATE SEQUENCE public.portfolios_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.portfolios_id_seq OWNER TO huguesmarie;

--
-- TOC entry 3999 (class 0 OID 0)
-- Dependencies: 221
-- Name: portfolios_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: huguesmarie
--

ALTER SEQUENCE public.portfolios_id_seq OWNED BY public.portfolios.id;


--
-- TOC entry 220 (class 1259 OID 16499)
-- Name: subscriptions; Type: TABLE; Schema: public; Owner: huguesmarie
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


ALTER TABLE public.subscriptions OWNER TO huguesmarie;

--
-- TOC entry 4000 (class 0 OID 0)
-- Dependencies: 220
-- Name: TABLE subscriptions; Type: COMMENT; Schema: public; Owner: huguesmarie
--

COMMENT ON TABLE public.subscriptions IS 'Subscription management for different tiers';


--
-- TOC entry 219 (class 1259 OID 16498)
-- Name: subscriptions_id_seq; Type: SEQUENCE; Schema: public; Owner: huguesmarie
--

CREATE SEQUENCE public.subscriptions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.subscriptions_id_seq OWNER TO huguesmarie;

--
-- TOC entry 4001 (class 0 OID 0)
-- Dependencies: 219
-- Name: subscriptions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: huguesmarie
--

ALTER SEQUENCE public.subscriptions_id_seq OWNED BY public.subscriptions.id;


--
-- TOC entry 216 (class 1259 OID 16390)
-- Name: users; Type: TABLE; Schema: public; Owner: huguesmarie
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


ALTER TABLE public.users OWNER TO huguesmarie;

--
-- TOC entry 4002 (class 0 OID 0)
-- Dependencies: 216
-- Name: TABLE users; Type: COMMENT; Schema: public; Owner: huguesmarie
--

COMMENT ON TABLE public.users IS 'Main user table with prospect and client management';


--
-- TOC entry 215 (class 1259 OID 16389)
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: huguesmarie
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO huguesmarie;

--
-- TOC entry 4003 (class 0 OID 0)
-- Dependencies: 215
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: huguesmarie
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- TOC entry 3725 (class 2604 OID 16694)
-- Name: apprentissages id; Type: DEFAULT; Schema: public; Owner: huguesmarie
--

ALTER TABLE ONLY public.apprentissages ALTER COLUMN id SET DEFAULT nextval('public.apprentissages_id_seq'::regclass);


--
-- TOC entry 3718 (class 2604 OID 16552)
-- Name: credits id; Type: DEFAULT; Schema: public; Owner: huguesmarie
--

ALTER TABLE ONLY public.credits ALTER COLUMN id SET DEFAULT nextval('public.credits_id_seq'::regclass);


--
-- TOC entry 3726 (class 2604 OID 16703)
-- Name: crypto_prices id; Type: DEFAULT; Schema: public; Owner: huguesmarie
--

ALTER TABLE ONLY public.crypto_prices ALTER COLUMN id SET DEFAULT nextval('public.crypto_prices_id_seq'::regclass);


--
-- TOC entry 3728 (class 2604 OID 16724)
-- Name: investment_plan_lines id; Type: DEFAULT; Schema: public; Owner: huguesmarie
--

ALTER TABLE ONLY public.investment_plan_lines ALTER COLUMN id SET DEFAULT nextval('public.investment_plan_lines_id_seq'::regclass);


--
-- TOC entry 3727 (class 2604 OID 16712)
-- Name: investment_plans id; Type: DEFAULT; Schema: public; Owner: huguesmarie
--

ALTER TABLE ONLY public.investment_plans ALTER COLUMN id SET DEFAULT nextval('public.investment_plans_id_seq'::regclass);


--
-- TOC entry 3628 (class 2604 OID 16415)
-- Name: investor_profiles id; Type: DEFAULT; Schema: public; Owner: huguesmarie
--

ALTER TABLE ONLY public.investor_profiles ALTER COLUMN id SET DEFAULT nextval('public.investor_profiles_id_seq'::regclass);


--
-- TOC entry 3721 (class 2604 OID 16567)
-- Name: payment_methods id; Type: DEFAULT; Schema: public; Owner: huguesmarie
--

ALTER TABLE ONLY public.payment_methods ALTER COLUMN id SET DEFAULT nextval('public.payment_methods_id_seq'::regclass);


--
-- TOC entry 3716 (class 2604 OID 16537)
-- Name: portfolio_holdings id; Type: DEFAULT; Schema: public; Owner: huguesmarie
--

ALTER TABLE ONLY public.portfolio_holdings ALTER COLUMN id SET DEFAULT nextval('public.portfolio_holdings_id_seq'::regclass);


--
-- TOC entry 3709 (class 2604 OID 16522)
-- Name: portfolios id; Type: DEFAULT; Schema: public; Owner: huguesmarie
--

ALTER TABLE ONLY public.portfolios ALTER COLUMN id SET DEFAULT nextval('public.portfolios_id_seq'::regclass);


--
-- TOC entry 3702 (class 2604 OID 16502)
-- Name: subscriptions id; Type: DEFAULT; Schema: public; Owner: huguesmarie
--

ALTER TABLE ONLY public.subscriptions ALTER COLUMN id SET DEFAULT nextval('public.subscriptions_id_seq'::regclass);


--
-- TOC entry 3618 (class 2604 OID 16393)
-- Name: users id; Type: DEFAULT; Schema: public; Owner: huguesmarie
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- TOC entry 3953 (class 0 OID 16691)
-- Dependencies: 230
-- Data for Name: apprentissages; Type: TABLE DATA; Schema: public; Owner: huguesmarie
--

COPY public.apprentissages (id, nom, description, fichier_pdf, image, date_creation, date_modification, actif, ordre, fichier_pdf_original) FROM stdin;
5	Qu’est-ce qu’une assurance-vie ?	assurance vie, descriptio,	c838e0da635f4e549e577ba5d559f5f2.pdf	9f5cc0d5758e4405b80a46b41e780040.png	2025-11-28 12:08:40.278508	2025-11-28 12:15:52.470181	t	1	\N
\.


--
-- TOC entry 3949 (class 0 OID 16549)
-- Dependencies: 226
-- Data for Name: credits; Type: TABLE DATA; Schema: public; Owner: huguesmarie
--

COPY public.credits (id, investor_profile_id, credit_type, description, initial_amount, remaining_amount, interest_rate, duration_years, monthly_payment, start_date, end_date, type_credit, montant_initial, montant_restant, taux_interet, duree_mois, mensualite, date_debut, date_fin, created_date, updated_date, calculated_monthly_payment, calculated_remaining_capital, last_calculation_date) FROM stdin;
\.


--
-- TOC entry 3955 (class 0 OID 16700)
-- Dependencies: 232
-- Data for Name: crypto_prices; Type: TABLE DATA; Schema: public; Owner: huguesmarie
--

COPY public.crypto_prices (id, symbol, price_usd, price_eur, updated_at, created_at) FROM stdin;
108	bitcoin	88597.39	75396.37888999999	2025-12-23 01:28:21.448646	2025-12-17 15:48:02.309696
109	btc	88597.39	75396.37888999999	2025-12-23 01:28:21.448646	2025-12-17 15:48:02.807122
130	uniswap	6.076	5.170675999999999	2025-12-23 01:28:21.448646	2025-12-17 15:48:13.620177
131	uni	6.076	5.170675999999999	2025-12-23 01:28:21.448646	2025-12-17 15:48:14.1187
132	aave	149.85	127.52234999999999	2025-12-23 01:28:21.448646	2025-12-17 15:48:14.614105
133	compound-governance-token	24.43	20.78993	2025-12-23 01:28:21.448646	2025-12-17 15:48:15.114605
134	comp	24.43	20.78993	2025-12-23 01:28:21.448646	2025-12-17 15:48:15.659253
135	maker	1813.7	1543.4587	2025-12-23 01:28:21.448646	2025-12-17 15:48:16.211605
136	mkr	1813.7	1543.4587	2025-12-23 01:28:21.448646	2025-12-17 15:48:16.758786
137	sushiswap	0.2957	0.2516407	2025-12-23 01:28:21.448646	2025-12-17 15:48:17.248607
138	sushi	0.2957	0.2516407	2025-12-23 01:28:21.448646	2025-12-17 15:48:17.814685
139	curve-dao-token	0.3814	0.3245714	2025-12-23 01:28:21.448646	2025-12-17 15:48:18.301267
140	crv	0.3814	0.3245714	2025-12-23 01:28:21.448646	2025-12-17 15:48:18.793756
141	1inch	0.1534	0.1305434	2025-12-23 01:28:21.448646	2025-12-17 15:48:19.297647
142	tether	1.0003	0.8512552999999999	2025-12-23 01:28:21.448646	2025-12-17 15:48:19.798194
143	usdt	1.0003	0.8512552999999999	2025-12-23 01:28:21.448646	2025-12-17 15:48:20.289238
144	usd-coin	1.0003	0.8512552999999999	2025-12-23 01:28:21.448646	2025-12-17 15:48:20.7805
145	usdc	1.0003	0.8512552999999999	2025-12-23 01:28:21.448646	2025-12-17 15:48:21.274705
146	binance-usd	1.0003	0.8512552999999999	2025-12-23 01:28:21.448646	2025-12-17 15:48:21.813674
147	busd	1.0003	0.8512552999999999	2025-12-23 01:28:21.448646	2025-12-17 15:48:22.313603
148	dai	0	0	2025-12-23 01:28:21.448646	2025-12-17 15:48:22.811756
149	terrausd	0	0	2025-12-23 01:28:21.448646	2025-12-17 15:48:23.300462
150	ust	0	0	2025-12-23 01:28:21.448646	2025-12-17 15:48:23.816136
151	axie-infinity	0.849	0.722499	2025-12-23 01:28:21.448646	2025-12-17 15:48:24.306273
187	filecoin	1.299	1.105449	2025-12-23 01:28:21.448646	2025-12-17 15:48:42.550119
188	fil	1.299	1.105449	2025-12-23 01:28:21.448646	2025-12-17 15:48:43.087653
189	internet-computer	3.041	2.587891	2025-12-23 01:28:21.448646	2025-12-17 15:48:43.57379
190	icp	3.041	2.587891	2025-12-23 01:28:21.448646	2025-12-17 15:48:44.092282
191	hedera-hashgraph	0.11371	0.09676721	2025-12-23 01:28:21.448646	2025-12-17 15:48:44.592664
192	hbar	0.11371	0.09676721	2025-12-23 01:28:21.448646	2025-12-17 15:48:45.07944
193	elrond-egd-2	6.33	5.38683	2025-12-23 01:28:21.448646	2025-12-17 15:48:45.567394
194	egld	6.33	5.38683	2025-12-23 01:28:21.448646	2025-12-17 15:48:46.103233
195	stellar	0.22009999999999996	0.18730509999999997	2025-12-23 01:28:21.448646	2025-12-17 15:48:46.612288
196	xlm	0.22009999999999996	0.18730509999999997	2025-12-23 01:28:21.448646	2025-12-17 15:48:47.148251
197	wrapped-bitcoin	88420.81	75246.10931	2025-12-23 01:28:21.448646	2025-12-17 15:48:47.645723
198	shiba-inu	7.25e-06	6.16975e-06	2025-12-23 01:28:21.448646	2025-12-17 15:48:48.188136
199	near	1.499	1.275649	2025-12-23 01:28:21.448646	2025-12-17 15:48:48.66706
200	aptos	1.621	1.379471	2025-12-23 01:28:21.448646	2025-12-17 15:48:49.165715
201	arbitrum	0.1877	0.1597327	2025-12-23 01:28:21.448646	2025-12-17 15:48:49.659049
202	first-digital-usd	0.9996000000000002	0.8506596000000001	2025-12-23 01:28:21.448646	2025-12-17 15:48:50.149799
203	optimism	0.2718	0.23130179999999997	2025-12-23 01:28:21.448646	2025-12-17 15:48:50.643328
204	immutable-x	0.22699999999999998	0.193177	2025-12-23 01:28:21.448646	2025-12-17 15:48:51.143596
205	render-token	7.029999999999999	5.98253	2025-12-23 01:28:21.448646	2025-12-17 15:48:51.653744
206	the-graph	0.03767	0.03205717	2025-12-23 01:28:21.448646	2025-12-17 15:48:52.212953
207	injective-protocol	4.663	3.968213	2025-12-23 01:28:21.448646	2025-12-17 15:48:52.704711
208	sei-network	0.1125	0.0957375	2025-12-23 01:28:21.448646	2025-12-17 15:48:53.275083
209	bittensor	224.2	190.7942	2025-12-23 01:28:21.448646	2025-12-17 15:48:53.8194
210	rune	0.577	0.49102699999999994	2025-12-23 01:28:21.448646	2025-12-17 15:48:54.410671
211	stacks	0.2488	0.2117288	2025-12-23 01:28:21.448646	2025-12-17 15:48:54.413248
152	axs	0.849	0.722499	2025-12-23 01:28:21.448646	2025-12-17 15:48:24.818183
153	the-sandbox	0.1154	0.0982054	2025-12-23 01:28:21.448646	2025-12-17 15:48:25.307267
154	sand	0.1154	0.0982054	2025-12-23 01:28:21.448646	2025-12-17 15:48:25.816582
155	decentraland	0.1234	0.10501339999999999	2025-12-23 01:28:21.448646	2025-12-17 15:48:26.30853
156	mana	0.1234	0.10501339999999999	2025-12-23 01:28:21.448646	2025-12-17 15:48:26.845484
157	enjincoin	0.02712	0.023079119999999998	2025-12-23 01:28:21.448646	2025-12-17 15:48:27.339557
158	enj	0.02712	0.023079119999999998	2025-12-23 01:28:21.448646	2025-12-17 15:48:27.871538
159	gala	0.00621	0.00528471	2025-12-23 01:28:21.448646	2025-12-17 15:48:28.394795
160	flow	0.171	0.145521	2025-12-23 01:28:21.448646	2025-12-17 15:48:28.913305
161	litecoin	76.7	65.2717	2025-12-23 01:28:21.448646	2025-12-17 15:48:29.4093
162	ltc	76.7	65.2717	2025-12-23 01:28:21.448646	2025-12-17 15:48:29.931742
163	bitcoin-cash	589.9	502.00489999999996	2025-12-23 01:28:21.448646	2025-12-17 15:48:30.432895
164	bch	589.9	502.00489999999996	2025-12-23 01:28:21.448646	2025-12-17 15:48:30.926386
165	ethereum-classic	12.25	10.42475	2025-12-23 01:28:21.448646	2025-12-17 15:48:31.399717
166	etc	12.25	10.42475	2025-12-23 01:28:21.448646	2025-12-17 15:48:31.88682
167	monero	118.7	101.0137	2025-12-23 01:28:21.448646	2025-12-17 15:48:32.380265
168	xmr	118.7	101.0137	2025-12-23 01:28:21.448646	2025-12-17 15:48:32.867812
169	zcash	430.74	366.55974	2025-12-23 01:28:21.448646	2025-12-17 15:48:33.398936
170	zec	430.74	366.55974	2025-12-23 01:28:21.448646	2025-12-17 15:48:33.894085
171	dash	38.55	32.80605	2025-12-23 01:28:21.448646	2025-12-17 15:48:34.408111
172	neo	3.579	3.045729	2025-12-23 01:28:21.448646	2025-12-17 15:48:34.971632
173	iota	0.0857	0.0729307	2025-12-23 01:28:21.448646	2025-12-17 15:48:35.487912
174	miota	0.0857	0.0729307	2025-12-23 01:28:21.448646	2025-12-17 15:48:35.977887
175	polygon	0.37940000000000007	0.32286940000000003	2025-12-23 01:28:21.448646	2025-12-17 15:48:36.482326
176	matic	0.37940000000000007	0.32286940000000003	2025-12-23 01:28:21.448646	2025-12-17 15:48:36.97453
177	fantom	0.6994	0.5951894	2025-12-23 01:28:21.448646	2025-12-17 15:48:37.480606
178	ftm	0.6994	0.5951894	2025-12-23 01:28:21.448646	2025-12-17 15:48:37.971217
179	cosmos	1.955	1.663705	2025-12-23 01:28:21.448646	2025-12-17 15:48:38.48372
180	atom	1.955	1.663705	2025-12-23 01:28:21.448646	2025-12-17 15:48:38.98094
181	algorand	0.1118	0.0951418	2025-12-23 01:28:21.448646	2025-12-17 15:48:39.475066
182	algo	0.1118	0.0951418	2025-12-23 01:28:21.448646	2025-12-17 15:48:40.009866
183	vechain	0.010629999999999999	0.00904613	2025-12-23 01:28:21.448646	2025-12-17 15:48:40.507167
184	vet	0.010629999999999999	0.00904613	2025-12-23 01:28:21.448646	2025-12-17 15:48:41.031919
185	theta-token	0.279	0.23742900000000003	2025-12-23 01:28:21.448646	2025-12-17 15:48:41.526334
186	theta	0.279	0.23742900000000003	2025-12-23 01:28:21.448646	2025-12-17 15:48:42.060827
110	ethereum	3019.66	2569.7306599999997	2025-12-23 01:28:21.448646	2025-12-17 15:48:03.346367
111	eth	3019.66	2569.7306599999997	2025-12-23 01:28:21.448646	2025-12-17 15:48:03.864812
112	binancecoin	857.32	729.57932	2025-12-23 01:28:21.448646	2025-12-17 15:48:04.363598
113	bnb	857.32	729.57932	2025-12-23 01:28:21.448646	2025-12-17 15:48:04.889446
114	ripple	1.9016999999999997	1.6183466999999998	2025-12-23 01:28:21.448646	2025-12-17 15:48:05.384127
115	xrp	1.9016999999999997	1.6183466999999998	2025-12-23 01:28:21.448646	2025-12-17 15:48:05.8805
117	sol	126.36	107.53236	2025-12-23 01:28:21.448646	2025-12-17 15:48:06.882241
116	solana	126.36	107.53236	2025-12-23 01:28:21.448646	2025-12-17 15:48:06.38544
118	cardano	0.3699	0.3147849	2025-12-23 01:28:21.448646	2025-12-17 15:48:07.377506
119	ada	0.3699	0.3147849	2025-12-23 01:28:21.448646	2025-12-17 15:48:07.892344
120	avalanche-2	12.49	10.62899	2025-12-23 01:28:21.448646	2025-12-17 15:48:08.459233
121	avax	12.49	10.62899	2025-12-23 01:28:21.448646	2025-12-17 15:48:08.969544
122	dogecoin	0.13272	0.11294472	2025-12-23 01:28:21.448646	2025-12-17 15:48:09.460917
123	doge	0.13272	0.11294472	2025-12-23 01:28:21.448646	2025-12-17 15:48:09.957381
124	tron	0.2837	0.2414287	2025-12-23 01:28:21.448646	2025-12-17 15:48:10.448696
125	trx	0.2837	0.2414287	2025-12-23 01:28:21.448646	2025-12-17 15:48:10.94829
126	polkadot	1.7870000000000001	1.520737	2025-12-23 01:28:21.448646	2025-12-17 15:48:11.464267
127	dot	1.7870000000000001	1.520737	2025-12-23 01:28:21.448646	2025-12-17 15:48:12.008082
128	chainlink	12.61	10.73111	2025-12-23 01:28:21.448646	2025-12-17 15:48:12.544342
129	link	12.61	10.73111	2025-12-23 01:28:21.448646	2025-12-17 15:48:13.039378
\.


--
-- TOC entry 3959 (class 0 OID 16721)
-- Dependencies: 236
-- Data for Name: investment_plan_lines; Type: TABLE DATA; Schema: public; Owner: huguesmarie
--

COPY public.investment_plan_lines (id, plan_id, support_envelope, description, reference, percentage, order_index, created_at, updated_at) FROM stdin;
7	1	PEA	ETF World	HD665HHGG	65	0	2025-12-20 14:53:17.465924	2025-12-20 14:53:17.465933
8	1	PER	SCPI	J87GGH65B5	35	1	2025-12-20 14:53:17.465934	2025-12-20 14:53:17.465934
\.


--
-- TOC entry 3957 (class 0 OID 16709)
-- Dependencies: 234
-- Data for Name: investment_plans; Type: TABLE DATA; Schema: public; Owner: huguesmarie
--

COPY public.investment_plans (id, user_id, name, is_active, created_at, updated_at) FROM stdin;
1	2	Plan d'investissement principal	t	2025-12-20 14:12:27.178937	2025-12-20 14:12:27.178946
3	11	Mon plan d'investissement	t	2025-12-20 23:59:40.435941	2025-12-20 23:59:40.435948
4	12	Mon plan d'investissement	t	2025-12-21 00:02:06.683747	2025-12-21 00:02:06.683756
5	10	Mon plan d'investissement	t	2025-12-22 23:05:53.528445	2025-12-22 23:05:53.528455
6	13	Mon plan d'investissement	t	2025-12-22 23:20:28.73332	2025-12-22 23:20:28.733329
\.


--
-- TOC entry 3941 (class 0 OID 16412)
-- Dependencies: 218
-- Data for Name: investor_profiles; Type: TABLE DATA; Schema: public; Owner: huguesmarie
--

COPY public.investor_profiles (id, user_id, monthly_net_income, monthly_savings_capacity, current_savings, impots_mensuels, risk_tolerance, investment_experience, investment_goals, investment_horizon, civilite, date_naissance, lieu_naissance, nationalite, pays_residence, pays_residence_fiscal, family_situation, professional_situation, metier, objectif_premiers_pas, objectif_constituer_capital, objectif_diversifier, objectif_optimiser_rendement, objectif_preparer_retraite, objectif_securite_financiere, objectif_projet_immobilier, objectif_revenus_complementaires, objectif_transmettre_capital, objectif_proteger_famille, tolerance_risque, horizon_placement, besoin_liquidite, experience_investissement, attitude_volatilite, has_livret_a, livret_a_value, has_ldds, ldds_value, has_lep, lep_value, has_pel_cel, pel_cel_value, has_current_account, current_account_value, liquidites_personnalisees_json, has_pea, pea_value, has_per, per_value, has_life_insurance, life_insurance_value, has_pee, pee_value, has_scpi, scpi_value, placements_personnalises_json, has_real_estate, real_estate_value, has_immobilier, immobilier_value, immobilier_data_json, has_autres_biens, autres_biens_value, autres_biens_data_json, cryptomonnaies_data_json, credits_data_json, revenus_complementaires, revenus_complementaires_json, charges_mensuelles, charges_mensuelles_json, has_pel, pel_value, has_cel, cel_value, has_autres_livrets, autres_livrets_value, has_cto, cto_value, has_private_equity, private_equity_value, has_crowdfunding, crowdfunding_value, other_investments, objectif_constitution_epargne, objectif_retraite, objectif_transmission, objectif_defiscalisation, objectif_immobilier, profil_risque_connu, profil_risque_choisi, question_1_reponse, question_2_reponse, question_3_reponse, question_4_reponse, question_5_reponse, synthese_profil_risque, cryptos_json, liquidites_personnalisees_json_legacy, placements_personnalises_json_legacy, date_completed, last_updated, professional_situation_other, calculated_total_liquidites, calculated_total_placements, calculated_total_immobilier_net, calculated_total_cryptomonnaies, calculated_total_autres_biens, calculated_total_credits_consommation, calculated_total_actifs, calculated_patrimoine_total_net, last_calculation_date) FROM stdin;
1	2	4000.00	1000.00	0.00	0.00	modéré	débutant		court	M.	1998-12-13	KUALA LUMPUR	Française	France	\N	Célibataire	Salarié	Cadre Ingénieur	t	t	t	f	f	f	t	t	f	f	5	court	oui	débutant	investir_plus	t	4700.00	f	0.00	f	0.00	f	0.00	f	0.00	null	t	23000.00	f	0.00	f	0.00	f	0.00	f	0.00	null	t	250000.00	t	250000.00	[{"type": "investissement_locatif", "valeur": 250000.0, "surface": 43.0, "has_credit": true, "credit_date": "2025-10", "credit_taeg": 3.35, "description": "Appartement asnieres sur seine", "credit_duree": 25, "credit_montant": 215000.0, "calculated_valeur_nette": 38177.0}]	f	0.00	[{"name": "Voiture", "valeur": 4000.0}, {"name": "Scooter", "valeur": 4000.0}]	[{"symbol": "bitcoin", "quantity": 0.1, "last_updated": "2025-12-22T23:12:11.719868", "current_price": 75643.59655999999, "calculated_value": 7564.359655999999}, {"symbol": "binancecoin", "quantity": 1.5, "last_updated": "2025-12-22T23:12:11.719884", "current_price": 733.2017, "calculated_value": 1099.80255}, {"symbol": "ethereum", "quantity": 0.5, "last_updated": "2025-12-22T23:12:11.719891", "current_price": 2566.98736, "calculated_value": 1283.49368}, {"symbol": "solana", "quantity": 10.0, "last_updated": "2025-12-22T23:12:11.719898", "current_price": 107.15138, "calculated_value": 1071.5138}]	[{"id": "", "taux": 6.5, "duree": 5, "mensualite": 97.83, "date_depart": "2025-01", "description": "Crédit auto", "montant_initial": 5000.0, "montant_restant": 3826.03}]	1400.00	[{"name": "Loyers immobiliers", "amount": 1350.0}, {"name": "Dividendes", "amount": 50.0}]	226.00	[{"name": "parking auto", "amount": 126.0}, {"name": "Assurances", "amount": 100.0}]	f	0.00	f	0.00	f	0.00	t	2500.00	f	0.00	f	0.00	\N	f	f	f	f	f	f	\N	\N	\N	\N	\N	\N	\N	[{"symbol": "BTC", "quantity": 0.25}, {"symbol": "ETH", "quantity": 3.0}]	\N	\N	2025-10-05 13:09:41.395387+02	2025-12-23 00:12:11.71098+01	\N	4700	25500	38177.36	11019.17	8000	3826.03	87396.53	83570.5	2025-12-22 23:12:11.719974
4	13	5000.00	1000.00	0.00	0.00	modéré	intermédiaire		long	M.	1998-12-13	KUALA LUMPUR	Française	France	\N	Célibataire	Salarié	Cadre Ingénieur	f	f	f	t	t	t	f	f	f	f	15	long	non	intermédiaire	attendre	t	2000.00	f	0.00	f	0.00	f	0.00	f	0.00	\N	t	15000.00	f	0.00	f	0.00	f	0.00	f	0.00	\N	t	230000.00	t	230000.00	[{"type": "residence_principale", "valeur": 230000.0, "surface": 45.0, "has_credit": true, "credit_date": "2025-09", "credit_taeg": 3.5, "description": "Appartement asnieres sur seine", "credit_duree": 25, "credit_montant": 200000.0, "calculated_valeur_nette": 34005.0}]	f	0.00	[{"name": "Hugues Marie", "valeur": 1000.0}]	[{"symbol": "binancecoin", "quantity": 1.0, "last_updated": "2025-12-22T23:35:57.750433", "current_price": 733.2017, "calculated_value": 733.2017}]	[]	0.00	\N	0.00	\N	f	0.00	f	0.00	f	0.00	f	0.00	f	0.00	f	0.00	\N	f	f	f	f	f	f	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-22 23:15:44.149787+01	2025-12-23 00:35:57.742209+01	cadre	2000	15000	34005	733.2	1000	0	52738.2	52738.2	2025-12-22 23:35:57.750519
3	10	0.00	0.00	0.00	0.00	modere	debutant		long terme	\N	\N	\N	\N	\N	\N	Célibataire	Salarié	\N	f	f	f	f	f	f	f	f	f	f	\N	\N	\N	\N	\N	f	0.00	f	0.00	f	0.00	f	0.00	f	0.00	\N	f	0.00	f	0.00	f	0.00	f	0.00	f	0.00	\N	f	0.00	f	0.00	\N	f	0.00	\N	\N	\N	\N	\N	\N	\N	f	0.00	f	0.00	f	0.00	f	0.00	f	0.00	f	0.00	\N	f	f	f	f	f	f	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2025-12-22 23:05:17.777341+01	2025-12-23 00:13:57.926811+01	\N	0	0	0	0	0	0	0	0	2025-12-22 23:13:57.93143
\.


--
-- TOC entry 3951 (class 0 OID 16564)
-- Dependencies: 228
-- Data for Name: payment_methods; Type: TABLE DATA; Schema: public; Owner: huguesmarie
--

COPY public.payment_methods (id, user_id, method_type, provider, provider_id, is_default, is_active, created_date) FROM stdin;
\.


--
-- TOC entry 3947 (class 0 OID 16534)
-- Dependencies: 224
-- Data for Name: portfolio_holdings; Type: TABLE DATA; Schema: public; Owner: huguesmarie
--

COPY public.portfolio_holdings (id, portfolio_id, asset_type, symbol, quantity, purchase_price, current_price, purchase_date, last_updated) FROM stdin;
\.


--
-- TOC entry 3945 (class 0 OID 16519)
-- Dependencies: 222
-- Data for Name: portfolios; Type: TABLE DATA; Schema: public; Owner: huguesmarie
--

COPY public.portfolios (id, user_id, name, strategy, total_value, created_date, last_updated, cash_amount, invested_amount, monthly_contribution, target_allocation) FROM stdin;
\.


--
-- TOC entry 3943 (class 0 OID 16499)
-- Dependencies: 220
-- Data for Name: subscriptions; Type: TABLE DATA; Schema: public; Owner: huguesmarie
--

COPY public.subscriptions (id, user_id, status, tier, price, start_date, end_date, next_billing_date, trial_end_date, cancelled_date, created_date, last_payment_date, payment_method) FROM stdin;
1	2	active	optima	20.00	2025-11-14 13:09:41.39476+01	\N	2025-12-14 13:09:41.394764+01	\N	\N	2025-11-14 13:09:41.39521+01	2025-11-14 13:09:41.394768+01	simulation
11	10	active	initia	20.00	2025-12-22 23:05:17.744966+01	\N	2026-01-21 23:05:17.744968+01	\N	\N	2025-12-22 23:05:17.749056+01	2025-12-22 23:05:17.744972+01	card_simulation
12	13	active	initia	20.00	2025-12-22 23:15:44.1366+01	\N	2026-01-21 23:15:44.136602+01	\N	\N	2025-12-22 23:15:44.138227+01	2025-12-22 23:15:44.136604+01	card_simulation
\.


--
-- TOC entry 3939 (class 0 OID 16390)
-- Dependencies: 216
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: huguesmarie
--

COPY public.users (id, email, password_hash, first_name, last_name, phone, profile_picture, is_admin, is_active, date_created, last_login, user_type, is_prospect, prospect_source, prospect_status, prospect_notes, appointment_requested, appointment_status, assigned_to, last_contact, invitation_token, invitation_sent_at, invitation_expires_at, can_create_account, plan_selected, payment_completed) FROM stdin;
13	dimitri@yopmail.com	pbkdf2:sha256:600000$bwCdQ4lr4AkX7zJP$049c7e528bda7414ad438bf6608071340d569b873f524feb582760747741f24a	dimitri	dimitri	0659986846	\N	f	t	2025-12-21 00:08:33.294975+01	2025-12-22 23:15:23.097035+01	client	f	site_vitrine	converti	\N	t	en_attente	\N	\N	\N	2025-12-21 00:08:55.664374+01	\N	f	t	t
11	test@yopmail.com	pbkdf2:sha256:600000$qqCeegmrDEWbBQ8Y$efff9519245b55929bbb7ed67abc144ba29bc24b7a7a05d30960e5c547118931	test	test	0659986846	\N	f	t	2025-12-20 23:24:33.309854+01	2025-12-20 23:32:19.941248+01	prospect	t	site_vitrine	contacté	\N	t	en_attente	\N	\N	\N	2025-12-20 23:25:22.192517+01	\N	f	f	f
6	prospect.test@gmail.com	pbkdf2:sha256:1000000$EBOjl7uIoj1ejKUM$dd7a1511038d82fd62dc66f537a1abba1a184d514f2646a39cd382d11b71a1bb	Test	Prospect	0612345678	\N	f	t	2025-12-20 22:50:50.519377+01	\N	prospect	t	manual_test	nouveau	\N	f	en_attente	\N	\N	\N	\N	\N	f	f	f
7	john@yopmail.com	pbkdf2:sha256:600000$L2IIuOeO0nzGCuLB$cca60af39b63e688ca1eede390037cc56eb04793d90022c02eeb9b027d72ee21	john	doe	dz	\N	f	t	2025-12-20 22:52:15.288934+01	\N	prospect	t	site_vitrine	nouveau	\N	t	en_attente	\N	\N	\N	\N	\N	f	f	f
8	titi@yopmail.com	pbkdf2:sha256:600000$Ty624FjTintONPSY$e51bddf98a2625cba580e7a830f30c1ed7c24a3f81bd31d01b0e0dbb1814cb4f	titi	tiit	8778	\N	f	t	2025-12-20 22:56:14.791328+01	\N	prospect	t	site_vitrine	nouveau	\N	t	en_attente	\N	\N	\N	\N	\N	f	f	f
1	admin@gmail.com	scrypt:32768:8:1$AM8zxmOx1aAq6sNz$9dd7213b84b407e7ed1013449add9cd10e6e882912e5b13b8c36a475ebb0841d586bac1d9b9e22d26ff4d6c577940a689376b0030e0d604c58b095635fa77867	Admin	Système	\N	\N	t	t	2025-11-12 20:47:26.769589+01	2025-12-23 01:29:44.222776+01	client	f	\N	nouveau	\N	f	en_attente	\N	\N	\N	\N	\N	f	f	f
12	rick@yopmail.com	pbkdf2:sha256:600000$1TxaRgZssZV86twp$0199d7f589a27a1edee469c917d240e27cfc1039361d1218895b61bdd45b418c	rick	rick	0659986846	\N	f	t	2025-12-21 00:00:50.521514+01	2025-12-21 00:01:59.843873+01	prospect	t	site_vitrine	contacté	\N	t	en_attente	\N	\N	\N	2025-12-21 00:01:15.44842+01	\N	f	f	f
10	ale@yopmail.com	pbkdf2:sha256:600000$OdnuALdKp7JPsUcp$368666e6cba1596e7c0e48560bf3679ad371330bcb4a9fd86e9688bbfcca9783	Alex	Test	0612345678	\N	f	t	2025-12-20 23:07:23.543078+01	2025-12-20 23:22:46.333008+01	client	f	site_vitrine	converti	\N	f	en_attente	\N	\N	\N	2025-12-20 23:09:42.887976+01	\N	f	t	t
2	test.client@gmail.com	pbkdf2:sha256:600000$lL0ln4vnCMKTUKZm$9a355ae4b728bf2c1931687ec300db69b94bf0ee5f4e0c1892c8f30c62489d2c	Hugues	MARIE	0659986846	\N	f	t	2025-09-30 13:09:41.246738+02	2025-12-22 23:11:21.512208+01	client	f	\N	nouveau	\N	f	en_attente	\N	\N	\N	\N	\N	f	f	f
\.


--
-- TOC entry 4004 (class 0 OID 0)
-- Dependencies: 229
-- Name: apprentissages_id_seq; Type: SEQUENCE SET; Schema: public; Owner: huguesmarie
--

SELECT pg_catalog.setval('public.apprentissages_id_seq', 5, true);


--
-- TOC entry 4005 (class 0 OID 0)
-- Dependencies: 225
-- Name: credits_id_seq; Type: SEQUENCE SET; Schema: public; Owner: huguesmarie
--

SELECT pg_catalog.setval('public.credits_id_seq', 1, false);


--
-- TOC entry 4006 (class 0 OID 0)
-- Dependencies: 231
-- Name: crypto_prices_id_seq; Type: SEQUENCE SET; Schema: public; Owner: huguesmarie
--

SELECT pg_catalog.setval('public.crypto_prices_id_seq', 211, true);


--
-- TOC entry 4007 (class 0 OID 0)
-- Dependencies: 235
-- Name: investment_plan_lines_id_seq; Type: SEQUENCE SET; Schema: public; Owner: huguesmarie
--

SELECT pg_catalog.setval('public.investment_plan_lines_id_seq', 8, true);


--
-- TOC entry 4008 (class 0 OID 0)
-- Dependencies: 233
-- Name: investment_plans_id_seq; Type: SEQUENCE SET; Schema: public; Owner: huguesmarie
--

SELECT pg_catalog.setval('public.investment_plans_id_seq', 6, true);


--
-- TOC entry 4009 (class 0 OID 0)
-- Dependencies: 217
-- Name: investor_profiles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: huguesmarie
--

SELECT pg_catalog.setval('public.investor_profiles_id_seq', 4, true);


--
-- TOC entry 4010 (class 0 OID 0)
-- Dependencies: 227
-- Name: payment_methods_id_seq; Type: SEQUENCE SET; Schema: public; Owner: huguesmarie
--

SELECT pg_catalog.setval('public.payment_methods_id_seq', 1, false);


--
-- TOC entry 4011 (class 0 OID 0)
-- Dependencies: 223
-- Name: portfolio_holdings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: huguesmarie
--

SELECT pg_catalog.setval('public.portfolio_holdings_id_seq', 1, false);


--
-- TOC entry 4012 (class 0 OID 0)
-- Dependencies: 221
-- Name: portfolios_id_seq; Type: SEQUENCE SET; Schema: public; Owner: huguesmarie
--

SELECT pg_catalog.setval('public.portfolios_id_seq', 1, false);


--
-- TOC entry 4013 (class 0 OID 0)
-- Dependencies: 219
-- Name: subscriptions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: huguesmarie
--

SELECT pg_catalog.setval('public.subscriptions_id_seq', 12, true);


--
-- TOC entry 4014 (class 0 OID 0)
-- Dependencies: 215
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: huguesmarie
--

SELECT pg_catalog.setval('public.users_id_seq', 13, true);


--
-- TOC entry 3772 (class 2606 OID 16698)
-- Name: apprentissages apprentissages_pkey; Type: CONSTRAINT; Schema: public; Owner: huguesmarie
--

ALTER TABLE ONLY public.apprentissages
    ADD CONSTRAINT apprentissages_pkey PRIMARY KEY (id);


--
-- TOC entry 3766 (class 2606 OID 16556)
-- Name: credits credits_pkey; Type: CONSTRAINT; Schema: public; Owner: huguesmarie
--

ALTER TABLE ONLY public.credits
    ADD CONSTRAINT credits_pkey PRIMARY KEY (id);


--
-- TOC entry 3774 (class 2606 OID 16705)
-- Name: crypto_prices crypto_prices_pkey; Type: CONSTRAINT; Schema: public; Owner: huguesmarie
--

ALTER TABLE ONLY public.crypto_prices
    ADD CONSTRAINT crypto_prices_pkey PRIMARY KEY (id);


--
-- TOC entry 3782 (class 2606 OID 16726)
-- Name: investment_plan_lines investment_plan_lines_pkey; Type: CONSTRAINT; Schema: public; Owner: huguesmarie
--

ALTER TABLE ONLY public.investment_plan_lines
    ADD CONSTRAINT investment_plan_lines_pkey PRIMARY KEY (id);


--
-- TOC entry 3778 (class 2606 OID 16714)
-- Name: investment_plans investment_plans_pkey; Type: CONSTRAINT; Schema: public; Owner: huguesmarie
--

ALTER TABLE ONLY public.investment_plans
    ADD CONSTRAINT investment_plans_pkey PRIMARY KEY (id);


--
-- TOC entry 3754 (class 2606 OID 16484)
-- Name: investor_profiles investor_profiles_pkey; Type: CONSTRAINT; Schema: public; Owner: huguesmarie
--

ALTER TABLE ONLY public.investor_profiles
    ADD CONSTRAINT investor_profiles_pkey PRIMARY KEY (id);


--
-- TOC entry 3770 (class 2606 OID 16572)
-- Name: payment_methods payment_methods_pkey; Type: CONSTRAINT; Schema: public; Owner: huguesmarie
--

ALTER TABLE ONLY public.payment_methods
    ADD CONSTRAINT payment_methods_pkey PRIMARY KEY (id);


--
-- TOC entry 3764 (class 2606 OID 16540)
-- Name: portfolio_holdings portfolio_holdings_pkey; Type: CONSTRAINT; Schema: public; Owner: huguesmarie
--

ALTER TABLE ONLY public.portfolio_holdings
    ADD CONSTRAINT portfolio_holdings_pkey PRIMARY KEY (id);


--
-- TOC entry 3761 (class 2606 OID 16527)
-- Name: portfolios portfolios_pkey; Type: CONSTRAINT; Schema: public; Owner: huguesmarie
--

ALTER TABLE ONLY public.portfolios
    ADD CONSTRAINT portfolios_pkey PRIMARY KEY (id);


--
-- TOC entry 3758 (class 2606 OID 16510)
-- Name: subscriptions subscriptions_pkey; Type: CONSTRAINT; Schema: public; Owner: huguesmarie
--

ALTER TABLE ONLY public.subscriptions
    ADD CONSTRAINT subscriptions_pkey PRIMARY KEY (id);


--
-- TOC entry 3740 (class 2606 OID 16406)
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: huguesmarie
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- TOC entry 3742 (class 2606 OID 16408)
-- Name: users users_invitation_token_key; Type: CONSTRAINT; Schema: public; Owner: huguesmarie
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_invitation_token_key UNIQUE (invitation_token);


--
-- TOC entry 3744 (class 2606 OID 16404)
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: huguesmarie
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- TOC entry 3767 (class 1259 OID 16562)
-- Name: idx_credits_profile; Type: INDEX; Schema: public; Owner: huguesmarie
--

CREATE INDEX idx_credits_profile ON public.credits USING btree (investor_profile_id);


--
-- TOC entry 3776 (class 1259 OID 16734)
-- Name: idx_investment_plans_user_active; Type: INDEX; Schema: public; Owner: huguesmarie
--

CREATE INDEX idx_investment_plans_user_active ON public.investment_plans USING btree (user_id, is_active);


--
-- TOC entry 3745 (class 1259 OID 16497)
-- Name: idx_investor_charges_jsonb; Type: INDEX; Schema: public; Owner: huguesmarie
--

CREATE INDEX idx_investor_charges_jsonb ON public.investor_profiles USING gin (charges_mensuelles_json);


--
-- TOC entry 3746 (class 1259 OID 16495)
-- Name: idx_investor_crypto_jsonb; Type: INDEX; Schema: public; Owner: huguesmarie
--

CREATE INDEX idx_investor_crypto_jsonb ON public.investor_profiles USING gin (cryptomonnaies_data_json);


--
-- TOC entry 3747 (class 1259 OID 16494)
-- Name: idx_investor_immobilier_jsonb; Type: INDEX; Schema: public; Owner: huguesmarie
--

CREATE INDEX idx_investor_immobilier_jsonb ON public.investor_profiles USING gin (immobilier_data_json);


--
-- TOC entry 3748 (class 1259 OID 16492)
-- Name: idx_investor_liquidites_jsonb; Type: INDEX; Schema: public; Owner: huguesmarie
--

CREATE INDEX idx_investor_liquidites_jsonb ON public.investor_profiles USING gin (liquidites_personnalisees_json);


--
-- TOC entry 3749 (class 1259 OID 16493)
-- Name: idx_investor_placements_jsonb; Type: INDEX; Schema: public; Owner: huguesmarie
--

CREATE INDEX idx_investor_placements_jsonb ON public.investor_profiles USING gin (placements_personnalises_json);


--
-- TOC entry 3750 (class 1259 OID 16491)
-- Name: idx_investor_profiles_risk; Type: INDEX; Schema: public; Owner: huguesmarie
--

CREATE INDEX idx_investor_profiles_risk ON public.investor_profiles USING btree (risk_tolerance);


--
-- TOC entry 3751 (class 1259 OID 16490)
-- Name: idx_investor_profiles_user; Type: INDEX; Schema: public; Owner: huguesmarie
--

CREATE INDEX idx_investor_profiles_user ON public.investor_profiles USING btree (user_id);


--
-- TOC entry 3752 (class 1259 OID 16496)
-- Name: idx_investor_revenus_jsonb; Type: INDEX; Schema: public; Owner: huguesmarie
--

CREATE INDEX idx_investor_revenus_jsonb ON public.investor_profiles USING gin (revenus_complementaires_json);


--
-- TOC entry 3768 (class 1259 OID 16578)
-- Name: idx_payment_methods_user; Type: INDEX; Schema: public; Owner: huguesmarie
--

CREATE INDEX idx_payment_methods_user ON public.payment_methods USING btree (user_id);


--
-- TOC entry 3779 (class 1259 OID 16735)
-- Name: idx_plan_lines_plan_order; Type: INDEX; Schema: public; Owner: huguesmarie
--

CREATE INDEX idx_plan_lines_plan_order ON public.investment_plan_lines USING btree (plan_id, order_index);


--
-- TOC entry 3780 (class 1259 OID 16732)
-- Name: idx_plan_order; Type: INDEX; Schema: public; Owner: huguesmarie
--

CREATE INDEX idx_plan_order ON public.investment_plan_lines USING btree (plan_id, order_index);


--
-- TOC entry 3762 (class 1259 OID 16547)
-- Name: idx_portfolio_holdings_portfolio; Type: INDEX; Schema: public; Owner: huguesmarie
--

CREATE INDEX idx_portfolio_holdings_portfolio ON public.portfolio_holdings USING btree (portfolio_id);


--
-- TOC entry 3759 (class 1259 OID 16546)
-- Name: idx_portfolios_user; Type: INDEX; Schema: public; Owner: huguesmarie
--

CREATE INDEX idx_portfolios_user ON public.portfolios USING btree (user_id);


--
-- TOC entry 3755 (class 1259 OID 16517)
-- Name: idx_subscriptions_status; Type: INDEX; Schema: public; Owner: huguesmarie
--

CREATE INDEX idx_subscriptions_status ON public.subscriptions USING btree (status, tier);


--
-- TOC entry 3756 (class 1259 OID 16516)
-- Name: idx_subscriptions_user; Type: INDEX; Schema: public; Owner: huguesmarie
--

CREATE INDEX idx_subscriptions_user ON public.subscriptions USING btree (user_id);


--
-- TOC entry 3737 (class 1259 OID 16409)
-- Name: idx_users_email; Type: INDEX; Schema: public; Owner: huguesmarie
--

CREATE INDEX idx_users_email ON public.users USING btree (email);


--
-- TOC entry 3738 (class 1259 OID 16410)
-- Name: idx_users_type; Type: INDEX; Schema: public; Owner: huguesmarie
--

CREATE INDEX idx_users_type ON public.users USING btree (user_type, is_prospect);


--
-- TOC entry 3775 (class 1259 OID 16706)
-- Name: ix_crypto_prices_symbol; Type: INDEX; Schema: public; Owner: huguesmarie
--

CREATE UNIQUE INDEX ix_crypto_prices_symbol ON public.crypto_prices USING btree (symbol);


--
-- TOC entry 3794 (class 2620 OID 16740)
-- Name: investment_plan_lines trigger_investment_plan_lines_updated_at; Type: TRIGGER; Schema: public; Owner: huguesmarie
--

CREATE TRIGGER trigger_investment_plan_lines_updated_at BEFORE UPDATE ON public.investment_plan_lines FOR EACH ROW EXECUTE FUNCTION public.update_investment_plan_updated_at();


--
-- TOC entry 3793 (class 2620 OID 16739)
-- Name: investment_plans trigger_investment_plans_updated_at; Type: TRIGGER; Schema: public; Owner: huguesmarie
--

CREATE TRIGGER trigger_investment_plans_updated_at BEFORE UPDATE ON public.investment_plans FOR EACH ROW EXECUTE FUNCTION public.update_investment_plan_updated_at();


--
-- TOC entry 3791 (class 2620 OID 16585)
-- Name: investor_profiles update_investor_profiles_last_updated; Type: TRIGGER; Schema: public; Owner: huguesmarie
--

CREATE TRIGGER update_investor_profiles_last_updated BEFORE UPDATE ON public.investor_profiles FOR EACH ROW EXECUTE FUNCTION public.update_last_updated_column();


--
-- TOC entry 3792 (class 2620 OID 16586)
-- Name: portfolios update_portfolios_last_updated; Type: TRIGGER; Schema: public; Owner: huguesmarie
--

CREATE TRIGGER update_portfolios_last_updated BEFORE UPDATE ON public.portfolios FOR EACH ROW EXECUTE FUNCTION public.update_last_updated_column();


--
-- TOC entry 3787 (class 2606 OID 16557)
-- Name: credits credits_investor_profile_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: huguesmarie
--

ALTER TABLE ONLY public.credits
    ADD CONSTRAINT credits_investor_profile_id_fkey FOREIGN KEY (investor_profile_id) REFERENCES public.investor_profiles(id) ON DELETE CASCADE;


--
-- TOC entry 3790 (class 2606 OID 16727)
-- Name: investment_plan_lines investment_plan_lines_plan_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: huguesmarie
--

ALTER TABLE ONLY public.investment_plan_lines
    ADD CONSTRAINT investment_plan_lines_plan_id_fkey FOREIGN KEY (plan_id) REFERENCES public.investment_plans(id);


--
-- TOC entry 3789 (class 2606 OID 16715)
-- Name: investment_plans investment_plans_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: huguesmarie
--

ALTER TABLE ONLY public.investment_plans
    ADD CONSTRAINT investment_plans_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- TOC entry 3783 (class 2606 OID 16485)
-- Name: investor_profiles investor_profiles_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: huguesmarie
--

ALTER TABLE ONLY public.investor_profiles
    ADD CONSTRAINT investor_profiles_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- TOC entry 3788 (class 2606 OID 16573)
-- Name: payment_methods payment_methods_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: huguesmarie
--

ALTER TABLE ONLY public.payment_methods
    ADD CONSTRAINT payment_methods_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- TOC entry 3786 (class 2606 OID 16541)
-- Name: portfolio_holdings portfolio_holdings_portfolio_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: huguesmarie
--

ALTER TABLE ONLY public.portfolio_holdings
    ADD CONSTRAINT portfolio_holdings_portfolio_id_fkey FOREIGN KEY (portfolio_id) REFERENCES public.portfolios(id) ON DELETE CASCADE;


--
-- TOC entry 3785 (class 2606 OID 16528)
-- Name: portfolios portfolios_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: huguesmarie
--

ALTER TABLE ONLY public.portfolios
    ADD CONSTRAINT portfolios_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- TOC entry 3784 (class 2606 OID 16511)
-- Name: subscriptions subscriptions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: huguesmarie
--

ALTER TABLE ONLY public.subscriptions
    ADD CONSTRAINT subscriptions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


-- Completed on 2025-12-23 11:08:07 CET

--
-- PostgreSQL database dump complete
--

\unrestrict 3JqG1GcefMVzNQBSnbw8YqzzTiLIBbvOnN8QZKEHXZVW65vrUjfJ8WzJbc9KJMA

