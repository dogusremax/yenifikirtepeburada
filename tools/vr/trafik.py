# yol maskesi + yön dokusu: R=maske, G,B = yol yönü (cos2θ, sin2θ kodlu)
import cv2, numpy as np, sys
n = sys.argv[1]; im = cv2.imread(f'/home/user/mainwt/assets/vr/gece-deneme/s{n}/gece-4k.jpg').astype(np.float32)
hsv = cv2.cvtColor(im.astype(np.uint8), cv2.COLOR_BGR2HSV).astype(np.float32)
h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
H = im.shape[0]
road = np.clip((v - 150) / 70, 0, 1) * np.clip((s - 90) / 80, 0, 1) * ((h > 5) & (h < 28))
road[: int(H * .5)] = 0; road[int(H * .965):] = 0             # ufkun üstü ve dip noktası yok
# çizgisellik: yapı tensörü
g = cv2.GaussianBlur(v, (0, 0), 1.2); gx = cv2.Sobel(g, cv2.CV_32F, 1, 0); gy = cv2.Sobel(g, cv2.CV_32F, 0, 1)
J = [cv2.GaussianBlur(a, (0, 0), 4) for a in (gx * gx, gy * gy, gx * gy)]
th = .5 * np.arctan2(2 * J[2], J[0] - J[1]) + np.pi / 2       # kenara dik = yol yönü
coh = np.sqrt((J[0] - J[1]) ** 2 + 4 * J[2] ** 2) / (J[0] + J[1] + 1e-3)
road = cv2.GaussianBlur(road * np.clip(coh * 1.5, 0, 1), (0, 0), .8)
out = np.dstack([np.clip(road * 255, 0, 255), (np.sin(2 * th) * .5 + .5) * 255, (np.cos(2 * th) * .5 + .5) * 255])   # PNG: R=cos2θ G=sin2θ B=maske
out = cv2.resize(out, (2048, 1024), interpolation=cv2.INTER_AREA)
out[out[..., 0] < 3, 1:] = 128                                  # yol dışı: düz renk, dosya küçülür
out = np.round(out)
cv2.imwrite(f'/home/user/mainwt/assets/vr/gece-deneme/s{n}/trafik.png', out.astype(np.uint8), [cv2.IMWRITE_PNG_COMPRESSION, 9])
cv2.imwrite('/tmp/claude-0/-home-user/48fc8b42-38be-5d92-914e-71dc25789cf8/scratchpad/trafik-mask.jpg', cv2.resize((road * 255).astype(np.uint8), (2048, 1024)))
print(road.mean())
