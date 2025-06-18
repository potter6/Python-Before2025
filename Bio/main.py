# from dash import Dash, html, dcc, callback, Output, Input
# import plotly.express as px
# import pandas as pd
#
# df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv')
#
# app = Dash(__name__)
#
# app.layout = html.Div([
#     html.H1(children='Title of Dash App', style={'textAlign':'center'}),
#     dcc.Dropdown(df.country.unique(), 'Canada', id='dropdown-selection'),
#     dcc.Graph(id='graph-content')
# ])
#
# @callback(
#     Output('graph-content', 'figure'),
#     Input('dropdown-selection', 'value')
# )
# def update_graph(value):
#     dff = df[df.country==value]
#     return px.line(dff, x='year', y='pop')
#
# if __name__ == '__main__':
#     app.run_server(debug=True)

## LICENSE: WTFPL
import matplotlib.pyplot as plt
import scipy.fftpack
import numpy as np
import simpleaudio as sa

## %matplotlib inline

lf_sigFreq = 1000.0  # typical 440 Hz
lf_sigAmp = 0.99 # 0 dB
li_fsam = 44100  # 44100 samples per sec
li_durSec = 2  # Duration of li_durSec

# create a List or Array of li_durSec*sample_rate elements, from 0 to li_durSec
li_N =  li_durSec * li_fsam
Lfa_el = np.linspace(0, li_durSec, li_N, False)

t_scope = np.linspace (0, 2/lf_sigFreq, 2*int(li_fsam/lf_sigFreq), False)

# Cal the element value
lf_toneV =  np.sin(lf_sigFreq * Lfa_el * 2 * np.pi)*0.99 + (np.sin(3 * lf_sigFreq * Lfa_el * 2 * np.pi) )/3 + (np.sin(5 * lf_sigFreq * Lfa_el * 2 * np.pi) )/5 + (np.sin(7 * lf_sigFreq * Lfa_el * 2 * np.pi) )/7 + (np.sin(9 * lf_sigFreq * Lfa_el * 2 * np.pi) )/9 + (np.sin(11 * lf_sigFreq * Lfa_el * 2 * np.pi) )/11 + (np.sin(13 * lf_sigFreq * Lfa_el * 2 * np.pi) )/13 + (np.sin(15 * lf_sigFreq * Lfa_el * 2 * np.pi) )/15 + (np.sin(17 * lf_sigFreq * Lfa_el * 2 * np.pi) )/17

# limit amplitude in 16-bit dynamic range 2^15-1
list_el_buff = lf_sigAmp * lf_toneV *32767/ np.max(np.abs(lf_toneV))
yf = scipy.fftpack.fft(list_el_buff/32767)
# Convert to 16-bit WAVE data format
list_el_buff = list_el_buff.astype(np.int16)

# Play back
play_obj = sa.play_buffer(list_el_buff, 1, 2, li_fsam)

#
# https://stackoverflow.com/questions/34162443/why-do-many-examples-use-fig-ax-plt-subplots-in-matplotlib-pyplot-python
#
xf = np.linspace(0.0, li_fsam/2, li_N//2)

fig, ax = plt.subplots()
## nexttile
ax.plot(xf, 2.0/li_N * np.abs(yf[:li_N//2]))
plt.xlabel('Frequency [Hz]');
plt.ylabel('Amplitude [Peak]')
plt.grid()
# plt.grid()
# plt.show()
## title('Plot 1')



# nexttile
fig, ax = plt.subplots()
##ax.plot( Lfa_el, lf_toneV)
ax.plot( t_scope, lf_toneV[: (t_scope.size )])

#plt.xlabel('Time');
#plt.ylabel('Amplitude')
# title('Plot 2')

plt.grid()
plt.show()

# Wait until done and exit
play_obj.wait_done()