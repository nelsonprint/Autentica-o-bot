from iqoptionapi.stable_api import IQ_Option
import time

# Função para se conectar à IQ Option
def connect_to_iqoption(email, password):
    print(f"Tentando conectar com email: {email}")  # Debugging
    iq = IQ_Option(email, password)
    check, reason = iq.connect()
    if check:
        print("Conectado com sucesso à IQ Option")
    else:
        print(f"Erro ao conectar: {reason}")
        exit()
    return iq

# Função para selecionar a conta
def select_account(iq):
    print("Selecione a conta:")
    print("1: CONTA PRACTICE")
    print("2: CONTA REAL")
    choice = int(input("Digite o número da conta: "))
    if choice == 1:
        iq.change_balance("PRACTICE")
    elif choice == 2:
        iq.change_balance("REAL")
    else:
        print("Escolha inválida")
        exit()
    print(f"Conta selecionada: {iq.get_balance_mode()}")

# Função para definir ativos OTC e normais manualmente
def get_assets():
    otc_assets = ["EURUSD-OTC", "GBPUSD-OTC", "USDCHF-OTC", "AUDCAD-OTC", "EURGBP-OTC"]
    norm_assets = ["EURUSD", "GBPUSD", "USDCHF", "AUDCAD", "EURGBP"]
    return otc_assets, norm_assets

# Função para verificar a disponibilidade de um ativo
def is_asset_available(iq, asset):
    assets = iq.get_all_open_time()  # Obtemos todos os ativos disponíveis
    return asset in assets['digital']  # Verifica se o ativo está na lista de ativos digitais

# Função para determinar o tipo de ativo disponível
def determine_available_assets(iq):
    otc_assets, norm_assets = get_assets()
    available_otc = [asset for asset in otc_assets if is_asset_available(iq, asset)]
    available_norm = [asset for asset in norm_assets if is_asset_available(iq, asset)]
    
    if available_otc:
        return available_otc, "OTC"
    elif available_norm:
        return available_norm, "NORM"
    else:
        print("Nenhum ativo disponível.")
        exit()

# Função para verificar condições de sobrecompra/sobrevenda com suporte/resistência
def check_trading_conditions(iq, asset):
    candles = iq.get_candles(asset, 300, 10, time.time())
    
    if candles is None:
        print(f"Erro ao obter candles para {asset}")
        return "HOLD"

    close_prices = [candle['close'] for candle in candles]
    
    # Exemplo simples de cálculo de suporte e resistência
    resistance = max(close_prices)
    support = min(close_prices)

    rsi = calculate_rsi(close_prices)

    if rsi > 70 and close_prices[-1] >= resistance:
        return "SELL"
    elif rsi < 30 and close_prices[-1] <= support:
        return "BUY"
    else:
        return "HOLD"

# Função simples para calcular RSI
def calculate_rsi(prices, period=14):
    deltas = [prices[i+1] - prices[i] for i in range(len(prices)-1)]
    seed = deltas[:period]
    up = sum([d for d in seed if d > 0]) / period
    down = -sum([d for d in seed if d < 0]) / period
    rs = up / down
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Função principal encapsulando a lógica
def trading_bot(iq, assets):
    while True:
        for asset in assets:
            action = check_trading_conditions(iq, asset)
            if action == "BUY":
                print(f"Comprando {asset}")
                iq.buy(50, asset, "call", 1)  # "call" para compra
            elif action == "SELL":
                print(f"Vendendo {asset}")
                iq.buy(50, asset, "put", 1)   # "put" para venda
            else:
                print(f"Nenhuma ação para {asset}")

        # Define o intervalo de verificação em 60 segundos
        interval = 60
        print(f"Próxima verificação em {interval // 60} minuto(s)...")
        time.sleep(interval)  # Espera 60 segundos antes de verificar novamente

# Função principal
def main():
    email = "nelsonmacapa@gmail.com"
    password = "J0ao8597*"
    
    iq = connect_to_iqoption(email, password)
    select_account(iq)
    
    assets, asset_type = determine_available_assets(iq)
    print(f"Operando com ativos {asset_type}: {assets}")
    
    trading_bot(iq, assets)

if __name__ == "__main__":
    main()
