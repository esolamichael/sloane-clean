# MANUAL NETLIFY UPLOAD INSTRUCTIONS

Since automated deployments and CLI tools are not working, here's how to manually upload your files to Netlify:

## Step 1: Package the build directory

1. Open Finder and navigate to:
   `/Users/Mike/Desktop/clean-code/sloane-frontend-package/build`

2. Right-click on the build folder and select "Compress 'build'" to create build.zip

## Step 2: Upload to Netlify via the dashboard

1. Go to [Netlify Dashboard](https://app.netlify.com/)
2. Click on "Sites" in the top navigation
3. Look for a button that says "Add new site" or "New site from"
4. Select "Deploy manually"
5. Drag and drop the build.zip file you created

If you don't see "Deploy manually" option:

1. Click "Add new site" > "Import an existing project"
2. Select "Deploy manually" on the next screen
3. Drop your build.zip file into the upload area

## Step 3: Configure site settings

After upload:

1. Go to "Site settings" > "Domain management"
2. Set up your custom domain if needed
3. Go to "Site settings" > "Build & deploy" > "Post processing"
4. Enable "Asset optimization" if you want

## Step 4: Add redirects

For API redirects, add a _redirects file in your build folder with:

```
/api/*  https://clean-code-app-1744825963.uc.r.appspot.com/api/:splat  200
/*      /index.html                                                    200
```

Then recompress and upload again.

## Alternative: Use the public share URL

As a last resort, upload the build.zip file to a public file sharing service and share the URL here. I can help you with next steps.