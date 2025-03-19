from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd

# Inicializar o navegador
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Pesquisa no Google Maps
busca = "empresas em São José dos Campos"
url = f"https://www.google.com/maps/search/{busca.replace(' ', '+')}"
driver.get(url)
time.sleep(5)

# Rolar a página para carregar mais resultados
painel_lateral = driver.find_element(By.XPATH, '//div[@role="feed"]')

# Número mínimo de registros desejados
min_registros = 160
rolagens = 0

# Rolagem contínua até obter o número mínimo de registros
while True:
    empresas = driver.find_elements(By.CLASS_NAME, "hfpxzc")
    print(f"Empresas encontradas: {len(empresas)}")

    # Verificar se já atingiu o mínimo desejado
    if len(empresas) >= min_registros:
        break

    # Rolar para carregar mais empresas
    painel_lateral.send_keys(Keys.END)
    time.sleep(3)
    rolagens += 1

    # Limite de rolagens para evitar loop infinito
    if rolagens > 60:
        print("Limite de rolagens atingido. Interrompendo.")
        break

# Extrair links das empresas
links_empresas = [empresa.get_attribute('href') for empresa in empresas]

dados_empresas = []

# Visitar cada empresa
for link in links_empresas:
    driver.get(link)
    time.sleep(4)

    # Obter nome
    try:
        nome = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//h1[contains(@class, "DUwDvf")]'))
        ).text
    except:
        nome = "Nome não encontrado"

    # Obter telefone
    try:
        # Tentar clicar no botão de telefone se existir
        try:
            botao_telefone = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//button[contains(@data-item-id, "phone:tel")]'))
            )
            botao_telefone.click()
            time.sleep(1)  # Pequeno tempo para carregar o número
        except:
            pass

        # Tentar obter o telefone após o clique
        try:
            telefone = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '//button[contains(@data-item-id, "phone:tel")]/div'))
            ).text
        except:
            telefone = "Telefone não disponível"

    except Exception as e:
        print(f"Erro ao obter telefone: {str(e)}")
        telefone = "Telefone não disponível"

    dados_empresas.append((nome, telefone))
    print(f"Nome: {nome}, Telefone: {telefone}")

driver.quit()

# Criar o DataFrame e salvar como Excel
df = pd.DataFrame(dados_empresas, columns=["Nome", "Telefone"])
df.to_excel(r'C:\Users\IBRA\Desktop\webscrapping\telefones_empresas.xlsx', index=False)
print("Dados exportados para planilha telefones_empresas.xlsx")
