#!/bin/bash
set -e

# Build the Next.js application
cd cms_odoo/next-odoo-minimal
npm run build

# Clean and copy the build output
rm -rf /Users/sarkande/docker/CMS_ODOO_NEXT/odoodidonc/cms_sarkande/static/front/*
cp -r out/* /Users/sarkande/docker/CMS_ODOO_NEXT/odoodidonc/cms_sarkande/static/front/

echo "Build completed successfully!"