#!/usr/bin/env python3
# Test translation save functionality

def test_translation():
    # Get page
    page = env['cms.page'].search([], limit=1)
    print(f"Page: {page.name}")

    # Get French language
    lang = env['res.lang'].search([('code', '=', 'fr_FR')], limit=1)
    if not lang:
        print("No French language found, creating...")
        lang = env['res.lang'].search([('active', '=', True), ('code', '!=', 'en_US')], limit=1)
    print(f"Language: {lang.name} ({lang.code})")

    # Create wizard
    wizard = env['cms.page.translate.wizard'].create({
        'page_id': page.id,
        'lang_id': lang.id,
    })
    print(f"Wizard created: {wizard}")
    print(f"Translation lines: {len(wizard.translation_line_ids)}")

    # Display first line
    if wizard.translation_line_ids:
        line = wizard.translation_line_ids[0]
        print(f"\nFirst line:")
        print(f"  Block: {line.block_name}")
        print(f"  Field: {line.field_label}")
        print(f"  Source: {line.source_value[:50] if line.source_value else 'Empty'}...")
        print(f"  Component: {line.component_model}[{line.component_id}].{line.component_field}")

        # Try to save a test translation
        line.write({'translated_value': 'Test translation FR'})
        env.cr.commit()

        try:
            result = wizard.action_save_translations()
            env.cr.commit()
            print("\n✓ Save successful!")
            print(f"Result: {result}")

            # Check if translation was saved
            translation = env['ir.translation'].search([
                ('type', '=', 'model'),
                ('name', '=', f'{line.component_model},{line.component_field}'),
                ('res_id', '=', line.component_id),
                ('lang', '=', lang.code),
            ], limit=1)
            if translation:
                print(f"✓ Translation found in DB: {translation.value[:50]}...")
            else:
                print("✗ Translation not found in DB!")

        except Exception as e:
            print(f"\n✗ Save error: {e}")
            import traceback
            traceback.print_exc()
            env.cr.rollback()
    else:
        print("No translation lines found!")

test_translation()
