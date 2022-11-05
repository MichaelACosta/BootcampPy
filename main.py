import pandas as pd
import numpy as np
from pandas_datareader import data as pdr
from datetime import datetime
from datetime import timedelta
import mplfinance as mpf
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import matplotlib.dates as mdates
import mplcyberpunk
from bcb import currency
from bcb import sgs
from fpdf import FPDF
from matplotlib.dates import date2num
import warnings
warnings.filterwarnings('ignore')

#pegando dados do yahoo finance. 
tickers = ['^BVSP', '^GSPC']

today = datetime.now()
last_year = today - timedelta(days = 366)

market_data = pdr.get_data_yahoo(tickers, start = last_year, end = today)

#pegando fechamento de cada ativo

closing_data = market_data['Adj Close']
closing_data.columns = ["Ibov", "S&P500"]
closing_data = closing_data.dropna()

#pegando fechamento mensal e anual para calcular rentabilidades

annual_data = closing_data.resample("Y").last()

monthly_data = closing_data.resample("M").last()

#calculando rentabilidades

daily_return = closing_data.pct_change().dropna()

return_month_by_month = monthly_data.pct_change().dropna()

return_month_by_month = return_month_by_month.iloc[1: , :]

return_in_the_year = annual_data.pct_change().dropna()


closing_day = daily_return.iloc[-1, :]

#volatilidade ibov e S&P500

volatility_12m_ibov = daily_return['Ibov'].std() * np.sqrt(252)
volatility_12m_sp = daily_return['S&P500'].std() * np.sqrt(252)

fig, ax = plt.subplots()

plt.style.use("cyberpunk")

ax.plot(closing_data.index, closing_data['Ibov'])
ax.grid(False)
plt.savefig('ibov.png', dpi = 300)

plt.show()

fig, ax = plt.subplots()

plt.style.use("cyberpunk")

ax.plot(closing_data.index, closing_data['Ibov'])
ax.grid(False)
plt.savefig('ibov.png', dpi = 300)

plt.show()

fig, ax = plt.subplots()

plt.style.use("cyberpunk")

ax.plot(closing_data.index, closing_data['S&P500'])
ax.grid(False)
plt.savefig('sp.png', dpi = 300)

plt.show()

#pegando os dias úteis

initial_date = closing_data.index[0]

if datetime.now().hour < 10:

    end_date = closing_data.index[-1]
    
else:
    
    end_date = closing_data.index[-2]
    

initial_date = initial_date.strftime("%d/%m/%Y")
end_date = end_date.strftime("%d/%m/%Y")

#série selic

selic = sgs.get({'selic':432}, start = '2010-01-01')

fig, ax = plt.subplots()

plt.style.use("cyberpunk")

ax.plot(selic.index, selic['selic'])
ax.yaxis.set_major_formatter(mtick.PercentFormatter())
ax.grid(False)
plt.savefig('selic.png', dpi = 300)

plt.show()

# Série do IPCA e IGP-M
inflation = sgs.get({'ipca': 433,
             'igp-m': 189}, start = last_year + timedelta(180))

numeric_dates = date2num(inflation.index)

fig, ax = plt.subplots()

ax.bar(numeric_dates-7, inflation['ipca'], label = "IPCA", width=7)
ax.bar(numeric_dates, inflation['igp-m'], label = "IGP-M", width=7)

ax.yaxis.set_major_formatter(mtick.PercentFormatter())
ax.xaxis_date()
formato_data = mdates.DateFormatter('%b-%y')
ax.xaxis.set_major_formatter(formato_data)
ax.grid(False)
plt.axhline(y=0, color = 'w')
plt.legend()
plt.savefig('inflation.png', dpi = 300)

plt.show()

# Importas moedas 

dolar = currency.get('USD', start=last_year, end=datetime.now())

monthly_dolar = dolar.resample("M").last()
annual_dolar = dolar.resample("Y").last()

#calculando rentabilidades

daily_dolar = dolar.pct_change().dropna()
closing_day_dolar = daily_dolar.iloc[-1, :]

return_month_by_month_dolar = monthly_dolar.pct_change().dropna()
return_month_by_month_dolar = return_month_by_month_dolar.iloc[1: , :]

return_in_the_year_dolar = annual_dolar.pct_change().dropna()

#Volatilidade dolar

volatility_12m_dolar = daily_dolar['USD'].std() * np.sqrt(252)

fig, ax = plt.subplots()

plt.style.use("cyberpunk")

ax.plot(dolar.index, dolar['USD'])
ax.yaxis.set_major_formatter('R${x:1.2f}')
ax.grid(False)
plt.savefig('dolar.png', dpi = 300)

plt.show()

months = []

for indice in return_month_by_month.index:

    month = indice.strftime("%b")
    
    months.append(month)
    
class PDF(FPDF):
    
    def header(self):
        
        # self.image('logo.png', 10, 8, 40)
        self.set_font('Arial', 'B', 20)
        self.ln(15)
        self.set_draw_color(35, 155, 132) #cor RGB
        self.cell(15, ln = False)
        self.cell(150, 15, f"Relatório de mercado {end_date}", 
                  border = True, ln = True, align = "C")
        self.ln(5)
        
    def footer(self):
        
        self.set_y(-15) #espaço ate o final da folha
        self.set_font('Arial', 'I', 10)
        self.cell(0, 10, f"{self.page_no()}/{{nb}}", align = "C")

#Definindo config básicas do PDF

pdf = PDF("P", "mm", "Letter")
pdf.set_auto_page_break(auto = True, margin = 15)
pdf.alias_nb_pages()
pdf.add_page()
pdf.set_fill_color(255, 255, 255)
pdf.set_draw_color(35, 155, 132)

pdf.set_font('Arial', 'B', 18)
pdf.cell(0, 10, "1 - Ações e câmbio", ln = True,  border = False, fill = False)
pdf.ln(2)

pdf.set_font('Arial', '', 14)
pdf.cell(0, 15, "1.1 Fechamento do mercado", ln = True,  border = False, fill = True)

pdf.ln(7)

#fechamento ibov
pdf.set_font('Arial', '', 13)
pdf.cell(25, 15, " Ibovespa", ln = False,  border = True, fill = True)
pdf.cell(20, 15, f" {str(round(closing_day[0] * 100, 2))}%", ln = True, 
         border = True, fill = False)

#fechamento s&p500
pdf.cell(25, 15, " S&P500", ln = False,  border = True, fill = True)
pdf.cell(20, 15, f" {str(round(closing_day[1] * 100, 2))}%", ln = True,  border = True, fill = False)

#fechamento Dólar
pdf.cell(25, 15, " Dólar", ln = False,  border = True, fill = True)
pdf.cell(20, 15, f" {str(round(closing_day_dolar[0] * 100, 2))}%", ln = True,  border = True, fill = False)

pdf.ln(7)

#imagens
pdf.set_font('Arial', '', 14)
pdf.cell(0, 15, "   1.2 Gráficos Ibovespa, S&P500 e Dólar", ln = True,  border = False, fill = False)

pdf.cell(95, 15, "Ibovespa", ln = False,  border = False, fill = False, align = "C")
pdf.cell(100, 15, "S&P500", ln = True,  border = False, fill = False, align = "C")
pdf.image("ibov.png", w = 80, h = 70, x = 20, y = 160)
pdf.image("sp.png", w = 80, h = 70, x = 115, y = 160)

pdf.ln(130)

pdf.cell(0, 15, "Dólar", ln = True,  border = False, fill = False, align = "C")
pdf.image("dolar.png", w = 100, h = 75, x = 58)


pdf.ln(2)

pdf.set_font('Arial', '', 14)
pdf.cell(0, 15, "   1.3 Rentabilidade mês a mês", ln = True,  border = False, fill = False)

#escrevendo os months
pdf.cell(17, 10, "", ln = False,  border = False, fill = True, align = "C")

for month in months:
    
    pdf.cell(16, 10, month, ln = False,  border = True, fill = True, align = "C")

pdf.ln(10)

#escrevendo o ibov

pdf.cell(17, 10, "Ibov", ln = False,  border = True, fill = True, align = "C")

pdf.set_font('Arial', '', 12)
for rent in return_month_by_month['Ibov']:
    
    pdf.cell(16, 10, f" {str(round(rent * 100, 2))}%", ln = False,  border = True, align = "C")

pdf.ln(10)

#escrevendo o S&P

pdf.cell(17, 10, "S&P500", ln = False,  border = True, fill = True, align = "C")

pdf.set_font('Arial', '', 12)
for rent in return_month_by_month['S&P500']:
    
    pdf.cell(16, 10, f" {str(round(rent * 100, 2))}%", ln = False,  border = True, align = "C")

pdf.ln(10)

#escrevendo o Dólar

pdf.cell(17, 10, "Dólar", ln = False,  border = True, fill = True, align = "C")

pdf.set_font('Arial', '', 12)
for rent in return_month_by_month_dolar['USD']:
    
    pdf.cell(16, 10, f" {str(round(rent * 100, 2))}%", ln = False,  border = True, align = "C")

pdf.ln(10)

#rent anual
pdf.set_font('Arial', '', 14)
pdf.cell(0, 15, "   1.4 Rentabilidade no ano", ln = True,  border = False, fill = False)

#rent anual ibov
pdf.set_font('Arial', '', 13)
pdf.cell(25, 10, "Ibovespa", ln = False,  border = True, fill = True, align = "C")
pdf.cell(20, 10, f" {str(round(return_in_the_year.iloc[0, 0] * 100, 2))}%", ln = True,  border = True, align = "C")

#rent anual S&P
pdf.cell(25, 10, "S&P500", ln = False,  border = True, fill = True, align = "C")
pdf.cell(20, 10, f" {str(round(return_in_the_year.iloc[0, 1] * 100, 2))}%", ln = True,  border = True, align = "C")

#rent anual Dólar
pdf.cell(25, 10, "Dólar", ln = False,  border = True, fill = True, align = "C")
pdf.cell(20, 10, f" {str(round(return_in_the_year_dolar.iloc[0, 0] * 100, 2))}%", ln = True,  border = True, align = "C")


pdf.ln(20)

#volatilidade
pdf.set_font('Arial', '', 14)
pdf.cell(0, 15, "   1.5 Volatilidade 12M", ln = True,  border = False, fill = False)

#vol ibov
pdf.set_font('Arial', '', 13)
pdf.cell(25, 10, "Ibovespa", ln = False,  border = True, fill = True, align = "C")
pdf.cell(20, 10, f" {str(round(volatility_12m_ibov * 100, 2))}%", ln = True,  border = True, align = "C")

#vol s&p500
pdf.cell(25, 10, "S&P500", ln = False,  border = True, fill = True, align = "C")
pdf.cell(20, 10, f" {str(round(volatility_12m_sp * 100, 2))}%", ln = True,  border = True, align = "C")

#vol dolar
pdf.cell(25, 10, "Dólar", ln = False,  border = True, fill = True, align = "C")
pdf.cell(20, 10, f" {str(round(volatility_12m_dolar * 100, 2))}%", ln = True,  border = True, align = "C")

pdf.ln(7)

pdf.set_font('Arial', 'B', 18)
pdf.cell(0, 15, "2 - Dados econômicos", ln = True,  border = False, fill = False)

pdf.ln(10)

pdf.cell(0, 15, "2.1 Inflacão", ln = True,  border = False, fill = False)
pdf.image("inflation.png", w = 110, h = 90, x = 40)

pdf.cell(0, 15, "2.2 Selic", ln = True,  border = False, fill = False)
pdf.image("selic.png", w = 110, h = 90, x = 40)

pdf.output('analysis.pdf')
