import asyncio
import os
import json
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_openai import AzureChatOpenAI
from browser_use import Agent
from browser_use.browser.browser import Browser, BrowserConfig
from browser_use.browser.context import BrowserContextConfig
from types import SimpleNamespace

# Cargar variables de entorno
load_dotenv()

# Configurar LLM (Langchain con Azure OpenAI)

print(
	SimpleNamespace(
		api_key=os.getenv('AZURE_OPENAI_API_KEY'),
		azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT'),
		api_version=os.getenv('AZURE_OPENAI_API_VERSION'),
		azure_deployment=os.getenv('AZURE_OPENAI_CHAT_VERSION'),
	)
)
llm = AzureChatOpenAI(
	max_tokens=5000,
	temperature=0,
	max_retries=20,
	request_timeout=500,
	api_key=os.getenv('AZURE_OPENAI_API_KEY'),
	azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT'),
	api_version=os.getenv('AZURE_OPENAI_API_VERSION'),
	azure_deployment=os.getenv('AZURE_OPENAI_CHAT_VERSION'),
)
print(llm)

# Tarea a ejecutar
"""
Entra en https://acciona.service-now.com/sp/"""
task = """
Entra en https://acciona.service-now.com/now/nav/ui/classic/params/target/home.do

Estás en un ServiceNow de Acciona, ya estás logueado como usuario
Utiliza el buscador para saber el estado de los distintos tickets que hay abiertos para el usuario actual, utilizando "Búsqueda"
"""


# Modelo Pydantic para la salida
class DownloadURL(BaseModel):
	download_link: str


# Configuración del navegador
context_config = BrowserContextConfig(
	save_downloads_path='/home/julian/Downloads',
	# browser_window_size={"width": 2000, "height": 1100},
	cookies_file='/home/julian/Downloads/cookies.json',
)

config = BrowserConfig(
	headless=False,  # Cambiar a True si quieres que sea en segundo plano
	new_context_config=context_config,
	chrome_instance_path='/usr/bin/google-chrome',  # Linux
)

# Credenciales

# Crear navegador
browser = Browser(config=config)


# Función principal
async def main():
	agent = Agent(
		task=task,
		llm=llm,
		max_actions_per_step=8,
		use_vision=True,
		browser=browser,
		save_conversation_path='/home/julian/Downloads/',
	)

	# Ejecutar agente
	history = await agent.run()
	result = history.final_result()
	# result = True
	# if result:
	# 	try:
	# 		# parsed = json.loads(result)
	# 		download_url = 'https://ov.aliaraenergia.es/mis-movimientos/exportar-excel'  # parsed.get("download_link", None)
	# 		if download_url:
	# 			print(f'🔗 URL de descarga detectada: {download_url}')
	# 		else:
	# 			print(' No se encontró la URL de descarga en la respuesta.')
	# 	except json.JSONDecodeError:
	# 		print(f'Error: La respuesta no es un JSON válido: {result}')
	#
	# # Crear segundo agente para descargar el archivo
	# download_agent = Agent(
	# 	task=f'Accede a esta URL para que se inicie la descarga automaticamente {download_url}',
	# 	llm=llm,
	# 	browser=browser,
	# 	sensitive_data=sensitive_data,
	# )
	#
	# await download_agent.run()
	#
	# # Cerrar el navegador al finalizar
	# await browser.close()


# Ejecutar la función principal solo si se ejecuta este script directamente
if __name__ == '__main__':
	asyncio.run(main())
