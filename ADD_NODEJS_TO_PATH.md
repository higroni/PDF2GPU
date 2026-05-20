# 🔧 Dodavanje Node.js u PATH

Node.js je instaliran ali nije u PATH-u. Evo kako da ga dodaš:

## 🔍 Korak 1: Pronađi Node.js Instalaciju

Node.js je obično instaliran na jednoj od ovih lokacija:

```
C:\Program Files\nodejs\
C:\Program Files (x86)\nodejs\
C:\Users\[TvojeIme]\AppData\Roaming\npm\
%APPDATA%\nvm\
```

**Proveri gde je instaliran:**

1. Otvori File Explorer
2. Proveri svaku od gornjih lokacija
3. Traži `node.exe` i `npm.cmd`

## ➕ Korak 2: Dodaj u PATH

### Metoda 1: Kroz System Properties (GUI)

1. **Otvori System Properties**
   - Pritisni `Windows + R`
   - Ukucaj: `sysdm.cpl`
   - Pritisni Enter

2. **Otvori Environment Variables**
   - Klikni na tab "Advanced"
   - Klikni "Environment Variables..."

3. **Edituj PATH**
   - U "System variables" sekciji, pronađi "Path"
   - Klikni "Edit..."
   - Klikni "New"
   - Dodaj putanju do Node.js foldera (npr. `C:\Program Files\nodejs`)
   - Klikni "OK" na svim prozorima

4. **Restartuj Terminal**
   - Zatvori sve PowerShell/CMD prozore
   - Otvori novi terminal
   - Testiraj: `node --version`

### Metoda 2: Kroz PowerShell (Admin)

```powershell
# Otvori PowerShell kao Administrator

# Dodaj Node.js u PATH (zameni putanju ako je drugačija)
$nodePath = "C:\Program Files\nodejs"
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";$nodePath", "Machine")

# Restartuj terminal i testiraj
node --version
npm --version
```

### Metoda 3: Privremeno (samo za trenutnu sesiju)

```powershell
# Dodaj privremeno (samo za trenutni terminal)
$env:Path += ";C:\Program Files\nodejs"

# Testiraj
node --version
npm --version
```

## ✅ Korak 3: Verifikuj

```powershell
# Otvori NOVI PowerShell terminal
node --version
# Trebalo bi: v20.x.x ili slično

npm --version  
# Trebalo bi: 10.x.x ili slično

npx --version
# Trebalo bi: 10.x.x ili slično
```

## 🚀 Korak 4: Kreiraj React Frontend

Kada Node.js radi:

```powershell
cd D:\POSAO\OllamaProjects\PDF2GPU

# Kreiraj React app
npx create-react-app frontend --template typescript

# Ovo će trajati 2-3 minuta...
```

## 🆘 Ako i dalje ne radi

### Opcija A: Reinstaliraj Node.js

1. Deinstaliraj trenutnu verziju
2. Preuzmi novu sa https://nodejs.org/
3. Tokom instalacije, potvrdi "Add to PATH" opciju

### Opcija B: Koristi NVM

```powershell
# Instaliraj nvm-windows
# https://github.com/coreybutler/nvm-windows/releases

# Instaliraj Node.js kroz nvm
nvm install 20
nvm use 20
```

### Opcija C: Počni samo sa Backend-om

Ako ne želiš da se bakćeš sa Node.js sada:

```powershell
cd D:\POSAO\OllamaProjects\PDF2GPU

# Kreiraj samo backend strukturu
mkdir backend, backend\api, backend\services, backend\models, backend\utils
mkdir tests, tests\phase1_backend_core

# Počni sa FAZOM 1 - Backend Core
# Frontend dodaj kasnije
```

## 📝 Napomena

Backend može raditi potpuno nezavisno od frontend-a. Možeš:
1. Prvo razviti kompletan backend
2. Testirati ga sa Postman/curl
3. Dodati frontend kasnije kada rešiš Node.js problem

**Oba pristupa su validna!**