/**
 * Substrate Descriptions Database
 * Contains detailed information about each print substrate type
 */

const substrateDescriptions = {
    // Fine Art Paper - Hot Press
    "Hot Press": {
        title: "Hot Press Smooth Matte Fine Art Paper",
        description: "It is a high-quality, archival grade, acid-free, 100% cotton rag inkjet paper. It has an extremely high color gamut, black density, and D-Max for high contrast in both B&W and color reproduction prints. This is perfect for artists and photographers looking for an ultra smooth fine art finish.",
        specs: [
            "Weight: 330 gsm, 17 mil",
            "Texture: Very lightly textured",
            "Brightness/Color: Neutral white",
            "Finish: Matte",
            "Acidity: Acid-free",
            "Size Option: Customizable up to 43×110\""
        ]
    },
    
    // Fine Art Paper - Cold Press
    "Cold Press": {
        title: "Cold Press Textured Matte Fine Art Paper",
        description: "It is a high-quality, archival grade, acid-free, 100% cotton rag inkjet paper. It has an extremely high color gamut and black density, perfect for artists and photographers looking for a bright white, textured surface that replicates the look and feel of traditional watercolor papers.",
        specs: [
            "Weight: 340 gsm, 21 mil",
            "Texture: Heavily textured",
            "Brightness/Color: Neutral white",
            "Finish: Matte",
            "Acidity: Acid-free",
            "Size Option: Customizable up to 43×110\""
        ]
    },
    
    // Photo Paper - Semi-Glossy/Luster
    "Semi-glossy": {
        title: "Semi-Glossy / Luster Photo Paper",
        description: "It is a premium-quality photo paper with a resin coating that makes it feel thicker, heavier, and more durable than most mass-marketed photo papers. The coating helps eliminate glare and visibility of fingerprints, so the ink colors come through vividly with no interference from smudges or smears.",
        specs: [
            "Weight: 250 gsm, 9.5 mil",
            "Texture: Textured",
            "Brightness/Color: Bright white",
            "Finish: Satin",
            "Acidity: Acid-free",
            "Size Option: Customizable up to 43×110\""
        ]
    },
    
    // Photo Paper - Glossy
    "Glossy": {
        title: "Glossy Photo Paper",
        description: "It is a top-quality choice paper with an ultra-glossy finish, 10 mil thickness, and wide color gamut, that delivers lifelike images. Smudge and water-resistant, its smooth base, maximum ink coverage, and high D-Max ensures vivid, true-to-life prints. It is a favorite for luxuriant depth and vibrant colors for photos and artwork.",
        specs: [
            "Weight: 260 gsm, 10 mil",
            "Texture: Ultra-smooth",
            "Brightness/Color: Bright white",
            "Finish: High-gloss",
            "Acidity: Acid-free",
            "Size Option: Customizable up to 43×110\""
        ]
    },
    
    // Foam-Mounted (all types share same description)
    "Foam-mounted Hot Press": {
        title: "Foam-Mounted Fine Art Paper",
        description: "A foam-mounted print is a high-quality paper print affixed to a lightweight yet sturdy foamcore backing. This combination ensures the print remains smooth and durable, providing a professional and polished look. While a standard print is simply an image on paper, a mounted print is attached to a rigid backing, such as foamcore, which maintains shape and integrity, offering a superior presentation. Mounting elevates both visual appeal and durability, eliminating concerns of wrinkling and making prints more manageable, easier to showcase, and transport. *Note: We recommend framing foam-mounted prints larger than 16×24 to prevent them from warping over time.",
        specs: [
            "Backing: Lightweight, sturdy foamcore",
            "Display Options: Prop on shelves, hang with adhesive, or frame",
            "Benefits: Professional appearance, easy transport",
            "Recommendation: Frame prints larger than 16×24\""
        ]
    },
    "Foam-mounted Cold Press": {
        title: "Foam-Mounted Fine Art Paper",
        description: "A foam-mounted print is a high-quality paper print affixed to a lightweight yet sturdy foamcore backing. This combination ensures the print remains smooth and durable, providing a professional and polished look. While a standard print is simply an image on paper, a mounted print is attached to a rigid backing, such as foamcore, which maintains shape and integrity, offering a superior presentation. Mounting elevates both visual appeal and durability, eliminating concerns of wrinkling and making prints more manageable, easier to showcase, and transport. *Note: We recommend framing foam-mounted prints larger than 16×24 to prevent them from warping over time.",
        specs: [
            "Backing: Lightweight, sturdy foamcore",
            "Display Options: Prop on shelves, hang with adhesive, or frame",
            "Benefits: Professional appearance, easy transport",
            "Recommendation: Frame prints larger than 16×24\""
        ]
    },
    "Foam-mounted Semi-Glossy": {
        title: "Foam-Mounted Photo Paper",
        description: "A foam-mounted print is a high-quality paper print affixed to a lightweight yet sturdy foamcore backing. This combination ensures the print remains smooth and durable, providing a professional and polished look. While a standard print is simply an image on paper, a mounted print is attached to a rigid backing, such as foamcore, which maintains shape and integrity, offering a superior presentation. Mounting elevates both visual appeal and durability, eliminating concerns of wrinkling and making prints more manageable, easier to showcase, and transport. *Note: We recommend framing foam-mounted prints larger than 16×24 to prevent them from warping over time.",
        specs: [
            "Backing: Lightweight, sturdy foamcore",
            "Display Options: Prop on shelves, hang with adhesive, or frame",
            "Benefits: Professional appearance, easy transport",
            "Recommendation: Frame prints larger than 16×24\""
        ]
    },
    "Foam-mounted Glossy": {
        title: "Foam-Mounted Photo Paper",
        description: "A foam-mounted print is a high-quality paper print affixed to a lightweight yet sturdy foamcore backing. This combination ensures the print remains smooth and durable, providing a professional and polished look. While a standard print is simply an image on paper, a mounted print is attached to a rigid backing, such as foamcore, which maintains shape and integrity, offering a superior presentation. Mounting elevates both visual appeal and durability, eliminating concerns of wrinkling and making prints more manageable, easier to showcase, and transport. *Note: We recommend framing foam-mounted prints larger than 16×24 to prevent them from warping over time.",
        specs: [
            "Backing: Lightweight, sturdy foamcore",
            "Display Options: Prop on shelves, hang with adhesive, or frame",
            "Benefits: Professional appearance, easy transport",
            "Recommendation: Frame prints larger than 16×24\""
        ]
    },
    
    // Canvas - 0.75"
    "0.75": {
        title: "0.75″ Stretched Canvas",
        description: "Highly recommended option for framing. Suitable for hanging directly onto walls with a small visible size profile.",
        specs: [
            "Material: Archival, Poly-Cotton Mix Canvas",
            "Hanging Option: Sawtooth or Hanging Wire",
            "Size Option: Customizable up to 36\" W x 48\" H"
        ]
    },
    
    // Canvas - 1.25"
    "1.25": {
        title: "1.25″ Stretched Canvas",
        description: "Provides a middle-ground between the 1.50 and 0.75. It's a cost-efficient option that allows for high-volume production.",
        specs: [
            "Material: Archival, Poly-Cotton Mix Canvas",
            "Hanging Option: Sawtooth only",
            "Size Option: Customizable up to 52\" W x 100\" H"
        ]
    },
    
    // Canvas - 1.50"
    "1.50": {
        title: "1.50″ Stretched Canvas",
        description: "Recommended option for hanging without framing. It has a thick profile that stands out against the wall.",
        specs: [
            "Material: Archival, Poly-Cotton Mix Canvas",
            "Hanging Option: Sawtooth or Hanging Wire",
            "Size Option: Customizable up to 52\" W x 100\" H"
        ]
    },
    
    // Framed Canvas (all types share same description)
    "Framed Canvas": {
        title: "Framed Canvas Prints",
        description: "Give your photos and artwork the professional look of a framed canvas print. Choose from floating, decorative, or traditional gallery frames – a perfect blend of elegance, depth, and versatility for any space. The vibrant, stunning colors of the print lure in viewers' eyes.",
        specs: [
            "Production Time: 2-3 business days",
            "Next Day and Same Day production available",
            "Printing Method: Giclee, Eco-Solvent Inkjet",
            "Available Sizes: 6×6\" to 52×100\"",
            "Standard, custom, and large print sizes available"
        ]
    },
    "Floating Frame": {
        title: "Framed Canvas Prints",
        description: "Give your photos and artwork the professional look of a framed canvas print. Choose from floating, decorative, or traditional gallery frames – a perfect blend of elegance, depth, and versatility for any space. The vibrant, stunning colors of the print lure in viewers' eyes.",
        specs: [
            "Production Time: 2-3 business days",
            "Next Day and Same Day production available",
            "Printing Method: Giclee, Eco-Solvent Inkjet",
            "Available Sizes: 6×6\" to 52×100\"",
            "Standard, custom, and large print sizes available"
        ]
    },
    "Gallery Frame": {
        title: "Framed Canvas Prints",
        description: "Give your photos and artwork the professional look of a framed canvas print. Choose from floating, decorative, or traditional gallery frames – a perfect blend of elegance, depth, and versatility for any space. The vibrant, stunning colors of the print lure in viewers' eyes.",
        specs: [
            "Production Time: 2-3 business days",
            "Next Day and Same Day production available",
            "Printing Method: Giclee, Eco-Solvent Inkjet",
            "Available Sizes: 6×6\" to 52×100\"",
            "Standard, custom, and large print sizes available"
        ]
    },
    
    // Metal Prints - Glossy White
    "Glossy White Metal": {
        title: "Glossy White Metal Prints",
        description: "Also known as Aluminum prints, metal prints are made from sleek aluminum sheets where the image is transferred through dye sublimation. This involves printing the image onto transfer paper before heating or baking it together with polymer-coated metal. As a result, the metal print finish is basically the ink that merges with the medium, making the output sturdy and incredibly vibrant. The glossy surface brings out the vibrancy of the print. The white base allows accurate color - the whites of the image appear white and the colors appear natural and how you expect them to be. It offers a vibrant look with rich color and high contrast.",
        specs: [
            "Surface: Glossy",
            "Base: White",
            "Sizes: Up to 40×60\"",
            "Method: Dye sublimation on polymer-coated aluminum"
        ]
    },
    
    // Metal Prints - Glossy Silver
    "Glossy Silver Metal": {
        title: "Glossy Silver Metal Prints",
        description: "Also known as Aluminum prints, metal prints are made from sleek aluminum sheets where the image is transferred through dye sublimation. This involves printing the image onto transfer paper before heating or baking it together with polymer-coated metal. As a result, the metal print finish is basically the ink that merges with the medium, making the output sturdy and incredibly vibrant. The glossy surface provides a vibrant, modern display. The silver base allows the aluminum to show through. Since the white point is the metal itself, the image will look darker and overall color accuracy will be reduced. It's highly recommended for high-contrast black and white images.",
        specs: [
            "Surface: Glossy",
            "Base: Silver",
            "Sizes: Up to 40×60\"",
            "Method: Dye sublimation on polymer-coated aluminum",
            "Best for: High-contrast B&W images"
        ]
    }
};

/**
 * Get description for a substrate option
 * @param {string} optionValue - The substrate option name (e.g., "Hot Press", "Aluminum")
 * @returns {object|null} - Description object or null if not found
 */
function getSubstrateDescription(optionValue) {
    if (!optionValue) return null;
    
    // Clean up the option value to match keys (remove parenthetical text like "(recommended for photos)")
    const cleanValue = optionValue.replace(/\s*\(.*?\)\s*/g, '').trim();
    
    // Try exact match first
    if (substrateDescriptions[cleanValue]) {
        return substrateDescriptions[cleanValue];
    }
    
    // Try case-insensitive match
    for (const key in substrateDescriptions) {
        if (key.toLowerCase() === cleanValue.toLowerCase()) {
            return substrateDescriptions[key];
        }
    }
    
    // Try partial match (for variations like "Printed Product - Hot Press" matching "Hot Press")
    for (const key in substrateDescriptions) {
        if (cleanValue.toLowerCase().includes(key.toLowerCase()) || 
            key.toLowerCase().includes(cleanValue.toLowerCase())) {
            return substrateDescriptions[key];
        }
    }
    
    console.log('[SUBSTRATE] No description found for:', optionValue, '(cleaned:', cleanValue + ')');
    return null;
}

// Export for use in other scripts
window.getSubstrateDescription = getSubstrateDescription;
