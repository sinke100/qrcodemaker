from flask import Flask, render_template, send_file, request, jsonify
import numpy as np
from base64 import b64encode as e, b64decode as d
import PIL.Image as im
from io import BytesIO as b
import segno

app = Flask(__name__)
app.template_folder = '.'

'''
save_qr(
        text="😀😎🚀🔥🍕🐱🎉💡🎲🌍👨‍💻👩‍🚀🧑‍🔬🏳️‍🌈🇭🇷",
        out_path="emoji_qr_a.png",
        error="M",
        border=1,
        scale=20,
        mode="P",
        fg=(200,150,0),
        bg=(250,200,0),
        ts=True
    )
request.form["text"]
request.form["out_path"]
request.form["error"]
int(request.form["border"])
int(request.form["scale"])
request.form["mode"]
tuple(map(int, request.form["fg"].split(",")))
tuple(map(int, request.form["bg"].split(",")))
ts = request.form["ts"] == "1"
'''
def process(d):
    l = 'text', 'out_path', 'error', 'border', 'scale', 'mode', 'fg', 'bg', 'ts'
    text, out_path, error, border, scale, mode, fg, bg, ts = [d.get(i) for i in l]
    out_path = out_path+'.png'
    ts = ts == '1'
    fg = tuple(map(int, fg.split(",")))
    bg = tuple(map(int, bg.split(",")))
    border = int(border)
    scale = int(scale)
    return return_qr(text=text,out_path=out_path,error=error,border=border,scale=scale,mode=mode,fg=fg,bg=bg,ts=ts)

def buffer(x):
    with b() as output:
        x.save(output,'PNG',optimize=True)
        data = output.getvalue()
    return data

def return_qr(out_path,text,error,border,scale,mode,fg,bg,ts):
    qr = segno.make_qr(text,error=error)
    matrix = qr.matrix_iter(scale=1, border=border)
    if mode == '1': data = [[int(not i) for i in t] for t in matrix]
    else: data = list(matrix)
    w, h = len(data[0]), len(data)
    data = np.kron(data, np.ones((scale, scale), dtype=np.uint8))
    img = im.new(mode,(w*scale,h*scale))
    img.putdata(data.flatten())
    if mode == 'P':
        img.putpalette(list(bg)+list(fg))
        if ts: img.info['transparency'] = 0
    data = buffer(img)
    mime_out = 'image/png'
    base64_data = e(data).decode()
    uri = f"data:{mime_out};base64,{base64_data}"
    main_dict = {'uri': uri, 'name': out_path}
    return jsonify(main_dict)

@app.route('/')
def index(): return render_template('index.html')

@app.route('/make_qr', methods=['POST'])
def make_qr(): return process(request.form)

if __name__ == '__main__': app.run(host='0.0.0.0')
