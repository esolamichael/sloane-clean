# DIRECT NETLIFY FIX - Missing build script

The build is failing because Netlify can't find the build script in package.json.

## Diagnosis
Error: `npm error Missing script: 'build'`

This means Netlify can't find the package.json or the package.json doesn't have a build script.

## Direct Fix in Netlify Dashboard

1. Log into Netlify Dashboard: https://app.netlify.com/
2. Go to your site settings
3. Navigate to "Build & deploy" -> "Build settings"
4. Update the following:
   - Base directory: `sloane-frontend-package`
   - Build command: `npm run build`
   - Publish directory: `sloane-frontend-package/build`
5. Save changes
6. Deploy site

## Verify Package.json

The package.json in sloane-frontend-package directory DOES have a build script:
```json
"scripts": {
  "start": "react-scripts start",
  "build": "react-scripts build",
  "test": "react-scripts test",
  "eject": "react-scripts eject"
}
```

## Manual Netlify Deploy

If that still doesn't work, try a direct manual deploy:

1. Build locally:
```bash
cd sloane-frontend-package
npm install --legacy-peer-deps
npm run build
```

2. Upload the build folder directly to Netlify:
   - Go to Netlify Dashboard
   - Click on your site
   - Click on "Deploys" tab
   - Drag and drop the `sloane-frontend-package/build` folder onto the dropzone that says "Drag and drop your site folder here"