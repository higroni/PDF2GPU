# 🔧 VSCode Terminal - Node.js PATH Problem

## Problem

Node.js radi u PowerShell-u ali **ne radi u VSCode terminalu**.

## Uzrok

VSCode terminal učitava PATH pri pokretanju VSCode-a. Ako si dodao Node.js u PATH posle pokretanja VSCode-a, terminal neće videti promene.

## ✅ Rešenje

### Metoda 1: Restartuj VSCode (Najbrže)

1. **Zatvori VSCode potpuno**
   - File → Exit (ili Alt+F4)
   - Proveri da nije otvoren u system tray-u

2. **Otvori VSCode ponovo**
   - Otvori novi terminal (Ctrl+`)
   - Testiraj: `node --version`

### Metoda 2: Reload Window

1. **Otvori Command Palette**
   - Pritisni `Ctrl+Shift+P`

2. **Reload Window**
   - Ukucaj: "Reload Window"
   - Izaberi: "Developer: Reload Window"

3. **Testiraj**
   - Otvori novi terminal (Ctrl+`)
   - `node --version`

### Metoda 3: Ručno Dodaj PATH u VSCode Settings

1. **Otvori Settings**
   - File → Preferences → Settings
   - Ili pritisni `Ctrl+,`

2. **Pronađi Terminal Settings**
   - Pretraži: "terminal.integrated.env.windows"

3. **Dodaj Node.js PATH**
   - Klikni "Edit in settings.json"
   - Dodaj:
   ```json
   {
     "terminal.integrated.env.windows": {
       "PATH": "${env:PATH};C:\\Program Files\\nodejs"
     }
   }
   ```

4. **Restartuj Terminal**
   - Zatvori sve terminale
   - Otvori novi (Ctrl+`)

### Metoda 4: Koristi PowerShell Profile

1. **Kreiraj PowerShell Profile**
   ```powershell
   # U VSCode terminalu
   notepad $PROFILE
   ```

2. **Dodaj Node.js PATH**
   ```powershell
   # Dodaj ovu liniju u profile
   $env:Path += ";C:\Program Files\nodejs"
   ```

3. **Sačuvaj i Zatvori**

4. **Reload Profile**
   ```powershell
   . $PROFILE
   ```

## 🧪 Verifikacija

```powershell
# U VSCode terminalu
node --version
npm --version
npx --version

# Sve tri komande treba da rade!
```

## 🚀 Kada Radi - Kreiraj Frontend

```powershell
cd D:\POSAO\OllamaProjects\PDF2GPU

# Kreiraj React app
npx create-react-app frontend --template typescript

# Čekaj 2-3 minuta...
# Kada završi:
cd frontend
npm start
```

## 💡 Pro Tip

Ako često imaš ovaj problem, dodaj Node.js PATH u **System Environment Variables** (ne User):

1. Windows + R → `sysdm.cpl`
2. Advanced → Environment Variables
3. U **System variables** (ne User), edituj Path
4. Dodaj `C:\Program Files\nodejs`
5. Restartuj računar (ili se odjavi/prijavi)

## 🆘 Ako Ništa Ne Radi

**Plan B: Koristi eksterni PowerShell**

1. Otvori PowerShell van VSCode-a
2. Navigiraj do projekta:
   ```powershell
   cd D:\POSAO\OllamaProjects\PDF2GPU
   ```
3. Pokreni komande tamo
4. Vrati se u VSCode za editovanje koda

**Plan C: Počni sa Backend-om**

Backend ne treba Node.js! Možeš početi sa FAZOM 1:

```powershell
# U VSCode terminalu (Python radi!)
cd D:\POSAO\OllamaProjects\PDF2GPU
mkdir backend
mkdir backend\api
mkdir backend\services
mkdir tests

# Počni sa backend implementacijom
```

Frontend dodaj kasnije kada rešiš Node.js problem.