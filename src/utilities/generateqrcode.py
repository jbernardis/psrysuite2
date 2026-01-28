
import qrcode

qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=3,
    border=4,
)
qr.add_data("ENGINEER: NONE")
qr.make(fit=True)
img = qr.make_image(fill_color="black", back_color="white")
# img = qrcode.make('TRAIN: CFYD')
type(img)  # qrcode.image.pil.PilImage
img.save("engineer-none.png")