import os
import sys
import time
from dotenv import load_dotenv
import google.generativeai as genai

# ==============================================================================
# SMOKE TEST v2 - GOOGLE GEMINI (AUTO-DETECT MODEL)
# ==============================================================================

def test_connection():
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        print("❌ ERRO CRÍTICO: GOOGLE_API_KEY não encontrada no .env")
        return

    print(f"🔐 Autenticando com API Key: {api_key[:8]}...")
    genai.configure(api_key=api_key)

    try:
        # 1. AUTO-DISCOVERY: Listar modelos disponíveis para sua conta
        print("🔍 Escaneando modelos disponíveis no seu projeto...")
        available_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)
                print(f"   - Encontrado: {m.name}")

        if not available_models:
            print("❌ ERRO: Nenhum modelo gerativo encontrado para essa chave.")
            return

        # 2. SELEÇÃO INTELIGENTE: Prioriza Gemini 1.5, senão usa o Pro padrão
        chosen_model = next((m for m in available_models if 'gemini-1.5' in m), None)
        if not chosen_model:
            chosen_model = next((m for m in available_models if 'gemini-pro' in m), available_models[0])
        
        print(f"\n🤖 Modelo selecionado automaticamente: '{chosen_model}'")

        # 3. TESTE DE GERAÇÃO
        model = genai.GenerativeModel(chosen_model)
        print("📡 Enviando ping de teste...")
        
        start_time = time.time()
        response = model.generate_content("Diga apenas: Sistema Operacional Online.")
        duration = time.time() - start_time

        print("\n" + "="*50)
        print(f"✅ CONEXÃO ESTABELECIDA ({duration:.2f}s)")
        print(f"🗣️  Resposta da IA: {response.text.strip()}")
        print("="*50 + "\n")

    except Exception as e:
        print(f"\n❌ FALHA NA CONEXÃO:\n{e}")

if __name__ == "__main__":
    test_connection()