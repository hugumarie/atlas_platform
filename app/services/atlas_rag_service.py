"""
Service RAG (Retrieval-Augmented Generation) pour l'Assistant Atlas.
Gère l'indexation et la recherche sémantique dans la base de connaissance Atlas.
"""

import os
import glob
import json
import hashlib
from typing import List, Dict, Any, Optional
from pathlib import Path
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle


class AtlasRAGService:
    """
    Service de recherche sémantique pour l'Assistant Atlas.
    
    Indexe et recherche dans les documents de la base de connaissance Atlas
    pour fournir un contexte pertinent aux réponses de l'IA.
    """
    
    def __init__(self):
        self.knowledge_base_path = os.path.join(os.path.dirname(__file__), '..', 'Atlas-knowledge')
        self.cache_path = os.path.join(os.path.dirname(__file__), '..', 'cache', 'rag_cache.pkl')
        self.system_prompt_path = os.path.join(self.knowledge_base_path, '_system:', 'Assistant_atlas.md')
        
        # État de l'index
        self.documents = []
        self.vectorizer = None
        self.document_vectors = None
        self.index_hash = None
        
        # Créer le dossier cache si nécessaire
        os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
        
        # Charger ou créer l'index
        self._load_or_build_index()
    
    def get_system_prompt(self) -> str:
        """
        Récupère le system prompt depuis assistant_atlas.md.
        
        Returns:
            str: Le contenu du system prompt
        """
        try:
            with open(self.system_prompt_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Enlever les métadonnées du début si présentes
                if content.startswith('# System Prompt'):
                    # Prendre tout après la première ligne de métadonnées
                    lines = content.split('\n')
                    # Chercher la première ligne qui commence par "Tu es"
                    start_idx = 0
                    for i, line in enumerate(lines):
                        if line.strip().startswith('Tu es'):
                            start_idx = i
                            break
                    content = '\n'.join(lines[start_idx:])
                return content.strip()
        except FileNotFoundError:
            print(f"⚠️ System prompt non trouvé : {self.system_prompt_path}")
            # Fallback vers un prompt de base
            return """Tu es Assistant Atlas, l'assistant officiel de la plateforme Atlas Invest.
Tu accompagnes des clients déjà abonnés à Atlas dans la compréhension de leur patrimoine et de leurs investissements.
Tu es un guide pédagogique, pas un robot-conseiller financier. Tu ne donnes jamais de conseil personnalisé d'investissement."""
    
    def _get_markdown_files(self) -> List[str]:
        """
        Récupère tous les fichiers .md de la base de connaissance (sauf _system).
        
        Returns:
            List[str]: Liste des chemins vers les fichiers markdown
        """
        markdown_files = []
        
        # Exclure le dossier _system du RAG
        exclude_patterns = ['_system:', '_system/', '_system\\']
        
        # Rechercher tous les fichiers .md
        pattern = os.path.join(self.knowledge_base_path, '**', '*.md')
        for file_path in glob.glob(pattern, recursive=True):
            # Vérifier qu'on n'est pas dans _system
            relative_path = os.path.relpath(file_path, self.knowledge_base_path)
            if not any(exclude in relative_path for exclude in exclude_patterns):
                markdown_files.append(file_path)
        
        return sorted(markdown_files)
    
    def _extract_content(self, file_path: str) -> Dict[str, Any]:
        """
        Extrait le contenu d'un fichier markdown avec métadonnées.
        
        Args:
            file_path (str): Chemin vers le fichier
            
        Returns:
            Dict[str, Any]: Document avec contenu et métadonnées
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extraire le nom du fichier et du dossier
            relative_path = os.path.relpath(file_path, self.knowledge_base_path)
            folder_name = os.path.dirname(relative_path)
            file_name = os.path.basename(file_path)
            
            # Extraire le titre (première ligne commençant par #)
            title = file_name.replace('.md', '').replace('_', ' ')
            lines = content.split('\n')
            for line in lines[:5]:  # Chercher dans les 5 premières lignes
                if line.strip().startswith('# '):
                    title = line.strip()[2:]
                    break
            
            # Découper le contenu en chunks si trop long
            chunks = self._split_content(content)
            
            documents = []
            for i, chunk in enumerate(chunks):
                doc = {
                    'content': chunk,
                    'title': title,
                    'file_path': file_path,
                    'folder': folder_name,
                    'file_name': file_name,
                    'chunk_index': i,
                    'total_chunks': len(chunks)
                }
                documents.append(doc)
            
            return documents
            
        except Exception as e:
            print(f"❌ Erreur lors de la lecture de {file_path}: {e}")
            return []
    
    def _split_content(self, content: str, max_length: int = 1000) -> List[str]:
        """
        Découpe le contenu en chunks plus petits si nécessaire.
        
        Args:
            content (str): Contenu à découper
            max_length (int): Taille maximale d'un chunk
            
        Returns:
            List[str]: Liste des chunks
        """
        if len(content) <= max_length:
            return [content]
        
        # Découper par paragraphes d'abord
        paragraphs = content.split('\n\n')
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            if len(current_chunk) + len(para) <= max_length:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = para + "\n\n"
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _calculate_content_hash(self) -> str:
        """
        Calcule un hash de tous les fichiers de la base de connaissance.
        Utilisé pour détecter les changements.
        
        Returns:
            str: Hash MD5 du contenu
        """
        hasher = hashlib.md5()
        
        for file_path in self._get_markdown_files():
            try:
                with open(file_path, 'rb') as f:
                    hasher.update(f.read())
            except Exception:
                continue
        
        return hasher.hexdigest()
    
    def _build_index(self):
        """
        Construit l'index de recherche sémantique.
        """
        print("🔄 Construction de l'index RAG Atlas...")
        
        # Récolter tous les documents
        self.documents = []
        markdown_files = self._get_markdown_files()
        
        for file_path in markdown_files:
            file_documents = self._extract_content(file_path)
            self.documents.extend(file_documents)
        
        print(f"📚 {len(self.documents)} chunks indexés depuis {len(markdown_files)} fichiers")
        
        if not self.documents:
            print("⚠️ Aucun document trouvé pour l'indexation")
            return
        
        # Créer les vecteurs TF-IDF
        texts = [doc['content'] for doc in self.documents]
        
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words=None,  # Pas de stop words français dans scikit-learn de base
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.95
        )
        
        self.document_vectors = self.vectorizer.fit_transform(texts)
        
        # Calculer et sauvegarder le hash
        self.index_hash = self._calculate_content_hash()
        
        # Sauvegarder l'index
        self._save_index()
        
        print("✅ Index RAG Atlas construit avec succès")
    
    def _save_index(self):
        """
        Sauvegarde l'index dans un fichier cache.
        """
        try:
            cache_data = {
                'documents': self.documents,
                'vectorizer': self.vectorizer,
                'document_vectors': self.document_vectors,
                'index_hash': self.index_hash
            }
            
            with open(self.cache_path, 'wb') as f:
                pickle.dump(cache_data, f)
                
        except Exception as e:
            print(f"⚠️ Erreur lors de la sauvegarde du cache RAG: {e}")
    
    def _load_index(self) -> bool:
        """
        Charge l'index depuis le cache si disponible.
        
        Returns:
            bool: True si chargé avec succès, False sinon
        """
        try:
            if not os.path.exists(self.cache_path):
                return False
            
            with open(self.cache_path, 'rb') as f:
                cache_data = pickle.load(f)
            
            self.documents = cache_data['documents']
            self.vectorizer = cache_data['vectorizer']
            self.document_vectors = cache_data['document_vectors']
            self.index_hash = cache_data['index_hash']
            
            return True
            
        except Exception as e:
            print(f"⚠️ Erreur lors du chargement du cache RAG: {e}")
            return False
    
    def _load_or_build_index(self):
        """
        Charge l'index depuis le cache ou le reconstruit si nécessaire.
        """
        current_hash = self._calculate_content_hash()
        
        # Essayer de charger le cache
        if self._load_index():
            # Vérifier si le contenu a changé
            if self.index_hash == current_hash:
                print("✅ Index RAG Atlas chargé depuis le cache")
                return
            else:
                print("🔄 Contenu modifié, reconstruction de l'index...")
        
        # Construire l'index
        self._build_index()
    
    def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Recherche les documents les plus pertinents pour une requête.
        
        Args:
            query (str): Requête de l'utilisateur
            max_results (int): Nombre maximum de résultats
            
        Returns:
            List[Dict[str, Any]]: Liste des documents pertinents avec scores
        """
        if not self.vectorizer or self.document_vectors is None:
            print("⚠️ Index RAG non disponible")
            return []
        
        try:
            # Vectoriser la requête
            query_vector = self.vectorizer.transform([query])
            
            # Calculer les similarités
            similarities = cosine_similarity(query_vector, self.document_vectors).flatten()
            
            # Trier par pertinence
            top_indices = similarities.argsort()[-max_results:][::-1]
            
            results = []
            for idx in top_indices:
                if similarities[idx] > 0.1:  # Seuil de pertinence minimum
                    doc = self.documents[idx].copy()
                    doc['relevance_score'] = similarities[idx]
                    results.append(doc)
            
            return results
            
        except Exception as e:
            print(f"❌ Erreur lors de la recherche RAG: {e}")
            return []
    
    def get_context_for_query(self, query: str, max_context_length: int = 2000) -> str:
        """
        Récupère le contexte le plus pertinent pour une requête.
        
        Args:
            query (str): Requête de l'utilisateur
            max_context_length (int): Taille maximale du contexte
            
        Returns:
            str: Contexte formaté pour l'IA
        """
        relevant_docs = self.search(query, max_results=3)
        
        if not relevant_docs:
            return ""
        
        context_parts = []
        current_length = 0
        
        for doc in relevant_docs:
            # Formater le contexte avec métadonnées
            doc_context = f"=== {doc['title']} ===\n{doc['content']}\n"
            
            if current_length + len(doc_context) > max_context_length:
                break
            
            context_parts.append(doc_context)
            current_length += len(doc_context)
        
        if context_parts:
            return "CONTEXTE ATLAS :\n" + "\n".join(context_parts)
        
        return ""
    
    def rebuild_index(self):
        """
        Force la reconstruction de l'index.
        """
        print("🔄 Reconstruction forcée de l'index RAG...")
        if os.path.exists(self.cache_path):
            os.remove(self.cache_path)
        self._build_index()


# Instance globale du service
_rag_service = None

def get_atlas_rag_service() -> AtlasRAGService:
    """
    Retourne l'instance du service RAG Atlas (singleton).
    
    Returns:
        AtlasRAGService: Instance du service
    """
    global _rag_service
    if _rag_service is None:
        _rag_service = AtlasRAGService()
    return _rag_service