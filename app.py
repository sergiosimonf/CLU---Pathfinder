import streamlit as st
import requests
import json
import uuid

SUBSCRIPTION_KEY = st.secrets["SUBSCRIPTION_KEY"]

def llamar_api(texto):
    """
    Llama a la API de análisis de conversaciones con el texto proporcionado.
    """
    reqUrl = "https://tradicionalia.cognitiveservices.azure.com/language/:analyze-conversations?api-version=2022-10-01-preview"
    
    # Generamos un identificador único para cada petición
    request_id = str(uuid.uuid4().int)
    
    headers = {
        "Ocp-Apim-Subscription-Key": SUBSCRIPTION_KEY,
        "Apim-Request-Id": request_id,
        "Content-Type": "application/json"
    }
    
    payload = {
        "kind": "Conversation",
        "analysisInput": {
            "conversationItem": {
                "id": request_id,
                "text": texto,
                "modality": "text",
                "language": "es",
                "participantId": request_id
            }
        },
        "parameters": {
            "projectName": "PathfinderClu",
            "verbose": True,
            "deploymentName": "production",
            "stringIndexType": "TextElement_V8"
        }
    }
    
    # Realizamos la petición POST a la API
    response = requests.post(reqUrl, headers=headers, data=json.dumps(payload))
    return response

def generar_respuesta(json_data):
    """
    Procesa el JSON obtenido de la API y genera un mensaje formateado.
    """
    result = json_data.get("result", {})
    query = result.get("query", "Consulta no especificada")
    prediction = result.get("prediction", {})
    top_intent = prediction.get("topIntent", "No identificado")
    entities = prediction.get("entities", [])
    
    # Extraer las entidades detectadas
    detalles = "\n".join([f"- {e['category'].capitalize()}: {e['text']}" for e in entities])
    
    # Formatear la respuesta con emojis y Markdown
    respuesta = (
        f"\U0001F4AC **Resultado de la consulta**\n\n"
        f"\U0001F4DD **Consulta:** _{query}_\n\n"
        f"\U0001F4A1 **Categoría principal detectada:** _{top_intent}_\n\n"
        f"\U0001F4CC **Detalles extraídos:**\n{detalles}\n\n"
        f"\u2728 ¿Necesitas más información? ¡Pregúntame!"
    )
    return respuesta

def main():
    st.title("Analizador de Conversaciones")
    st.write("Ingrese su consulta para analizarla:")
    
    st.markdown(
        """
        <style>
            #MainMenu, footer, header {visibility: hidden;}
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # Campo de entrada para la consulta
    consulta = st.text_input("Consulta", value="Que conjuros puede usar un mago de nivel 10")
    
    if st.button("Analizar"):
        # El spinner se mostrará mientras se realiza la llamada a la API
        with st.spinner("Realizando el análisis, por favor espere..."):
            response = llamar_api(consulta)
        
        if response.status_code != 200:
            st.error(f"Error al llamar a la API: {response.status_code}")
        else:
            try:
                json_data = response.json()
                mensaje = generar_respuesta(json_data)
                st.markdown(mensaje)
            except json.JSONDecodeError as e:
                st.error("Error al decodificar la respuesta JSON: " + str(e))
            except Exception as e:
                st.error("Ocurrió un error: " + str(e))

if __name__ == '__main__':
    main()