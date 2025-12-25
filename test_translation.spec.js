const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({
    headless: false,
    slowMo: 500
  });
  const context = await browser.newContext();
  const page = await context.newPage();

  // Listen to console messages and errors
  page.on('console', msg => {
    if (msg.type() === 'error') {
      console.log('BROWSER ERROR:', msg.text());
    }
  });

  page.on('pageerror', error => {
    console.log('PAGE ERROR:', error.message);
  });

  try {
    console.log('Opening Odoo backend in debug mode...');
    await page.goto('http://localhost:8219/odoo?debug=assets');
    await page.waitForTimeout(2000);

    const loginInput = await page.$('input[name="login"]');
    if (!loginInput) {
      console.log('Already logged in, continuing...');
    } else {
      console.log('Logging in...');
      await page.fill('input[name="login"]', 'odoo');
      await page.fill('input[name="password"]', 'odoo');
      await page.click('button[type="submit"]');
      await page.waitForTimeout(3000);
    }

    console.log('Navigating to CMS app...');
    // Close notification if present
    const closeButton = await page.$('button.btn-close');
    if (closeButton) {
      await closeButton.click();
      await page.waitForTimeout(300);
    }

    // Click on CMS app
    const cmsApp = await page.waitForSelector('.o_app[data-menu-xmlid*="cms"], .o_app:has-text("CMS")', { timeout: 5000 });
    await cmsApp.click();
    await page.waitForTimeout(2000);

    // Now navigate to Pages
    console.log('Navigating to CMS Pages...');
    const pagesMenu = await page.waitForSelector('a.dropdown-item:has-text("Pages"), a:has-text("CMS Pages")', { timeout: 5000 });
    await pagesMenu.click();
    await page.waitForTimeout(2000);

    console.log('Opening first page...');
    // Click on first page in list
    const firstPage = await page.waitForSelector('.o_data_row', { timeout: 5000 });
    await firstPage.click();
    await page.waitForTimeout(2000);

    console.log('Clicking Traduire button...');
    // Click on Traduire button
    const translateButton = await page.waitForSelector('button:has-text("Traduire")', { timeout: 5000 });
    await translateButton.click();
    await page.waitForTimeout(2000);

    // Check for errors
    const errorDialog = await page.$('.modal-dialog:has-text("Oops!")');
    if (errorDialog) {
      console.error('ERROR FOUND: Oops dialog appeared');

      // Click on "See technical details"
      const detailsButton = await page.$('a:has-text("See technical details")');
      if (detailsButton) {
        await detailsButton.click();
        await page.waitForTimeout(1000);

        // Get error details
        const errorDetails = await page.$('.o_error_detail');
        if (errorDetails) {
          const errorText = await errorDetails.textContent();
          console.error('ERROR DETAILS:', errorText);
        }
      }
    }

    // Take screenshot
    await page.screenshot({ path: '/Users/sarkande/docker/CMS_ODOO_NEXT/translation_wizard.png', fullPage: true });
    console.log('Screenshot saved to translation_wizard.png');

    // Wait to see the result
    await page.waitForTimeout(10000);

  } catch (error) {
    console.error('Test failed:', error.message);
    await page.screenshot({ path: '/Users/sarkande/docker/CMS_ODOO_NEXT/error_screenshot.png', fullPage: true });
    console.log('Error screenshot saved to error_screenshot.png');
  } finally {
    await browser.close();
  }
})();
