/**
 * Substrate Descriptions Database
 * Detailed information about each print substrate type
 */

const substrateDescriptions = {
    // Fine Art Paper Options
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
    "Cold Press": {
        title: "Cold Press Textured Matte Fine Art Paper",
        description: "This archival-grade, 100% cotton rag paper features a subtle texture that adds depth and character to your prints. Ideal for fine art photography and artwork that benefits from a traditional, painterly feel.",
        specs: [
            "Weight: 310 gsm, 16 mil",
            "Texture: Medium texture",
            "Brightness/Color: Warm white",
            "Finish: Matte",
            "Acidity: Acid-free",
            "Size Option: Customizable up to 43×110\""
        ]
    },
    "Semi-glossy": {
        title: "Semi-Glossy Fine Art Paper",
        description: "A premium archival paper with a subtle sheen that enhances color vibrancy while maintaining excellent detail. Perfect for photographs that need a balance between matte elegance and glossy pop.",
        specs: [
            "Weight: 300 gsm, 15 mil",
            "Texture: Smooth with slight sheen",
            "Brightness/Color: Bright white",
            "Finish: Semi-glossy",
            "Acidity: Acid-free",
            "Size Option: Customizable up to 43×110\""
        ]
    },
    "Glossy": {
        title: "Glossy Fine Art Paper",
        description: "High-gloss archival paper that delivers maximum color saturation and contrast. Excellent for vibrant, contemporary photography where bold colors and sharp details are paramount.",
        specs: [
            "Weight: 290 gsm, 14 mil",
            "Texture: Smooth glossy",
            "Brightness/Color: Ultra bright white",
            "Finish: High gloss",
            "Acidity: Acid-free",
            "Size Option: Customizable up to 43×110\""
        ]
    },
    
    // Metal Print Options
    "Aluminum": {
        title: "Aluminum Metal Print",
        description: "Your image is infused directly into specially coated aluminum sheets, creating a stunning, modern display with incredible depth and luminosity. The metal surface adds a contemporary edge and exceptional durability.",
        specs: [
            "Material: .045\" aluminum",
            "Finish: High gloss or matte available",
            "Mounting: Float mount hardware included",
            "Durability: Waterproof, scratch-resistant",
            "Vibrancy: Exceptional color depth",
            "Size Option: Customizable up to 48×96\""
        ]
    },
    "ChromaLuxe": {
        title: "ChromaLuxe Metal Print",
        description: "Premium metal printing on ChromaLuxe aluminum panels delivers museum-quality results with unparalleled color accuracy and longevity. The dye-sublimation process creates images that are embedded into the surface for permanent, fade-resistant beauty.",
        specs: [
            "Material: ChromaLuxe aluminum",
            "Finish: Gloss or matte",
            "Mounting: Ready to hang",
            "Durability: Lifetime guarantee",
            "Vibrancy: Maximum color gamut",
            "Size Option: Customizable up to 48×96\""
        ]
    },
    
    // Canvas Options
    "Gallery Wrap": {
        title: "Gallery Wrap Canvas",
        description: "Your image is printed on premium canvas and stretched around a 1.5\" wooden frame. The image wraps around the edges for a seamless, frameless presentation that's ready to hang.",
        specs: [
            "Material: Premium poly-cotton blend canvas",
            "Frame: 1.5\" stretcher bars",
            "Edges: Image wrapped around sides",
            "Finish: Matte or satin coating",
            "Mounting: Ready to hang",
            "Size Option: Customizable up to 60×120\""
        ]
    },
    "Museum Wrap": {
        title: "Museum Wrap Canvas",
        description: "Similar to gallery wrap but with deeper 2.5\" stretcher bars for a more substantial, gallery-quality presentation. The extra depth creates dramatic shadows and a premium aesthetic.",
        specs: [
            "Material: Premium poly-cotton blend canvas",
            "Frame: 2.5\" stretcher bars",
            "Edges: Image wrapped around sides",
            "Finish: Matte or satin coating",
            "Mounting: Ready to hang",
            "Size Option: Customizable up to 60×120\""
        ]
    },
    
    // Framed Canvas Options
    "Black Frame": {
        title: "Framed Canvas - Black Frame",
        description: "Your canvas print is elegantly framed in a sleek black wooden frame, adding a classic, sophisticated touch. The frame complements any decor while protecting and enhancing your artwork.",
        specs: [
            "Frame Material: Solid wood",
            "Frame Color: Matte black",
            "Frame Width: 1.5\"",
            "Canvas: Gallery wrap style",
            "Mounting: Ready to hang",
            "Size Option: Customizable up to 48×96\""
        ]
    },
    "White Frame": {
        title: "Framed Canvas - White Frame",
        description: "A clean, contemporary white wooden frame surrounds your canvas print, creating a bright, modern presentation perfect for light, airy spaces.",
        specs: [
            "Frame Material: Solid wood",
            "Frame Color: Matte white",
            "Frame Width: 1.5\"",
            "Canvas: Gallery wrap style",
            "Mounting: Ready to hang",
            "Size Option: Customizable up to 48×96\""
        ]
    },
    "Natural Wood Frame": {
        title: "Framed Canvas - Natural Wood Frame",
        description: "Warm, natural wood framing adds an organic, rustic charm to your canvas print. The visible wood grain brings texture and character to your display.",
        specs: [
            "Frame Material: Solid wood",
            "Frame Color: Natural wood finish",
            "Frame Width: 1.5\"",
            "Canvas: Gallery wrap style",
            "Mounting: Ready to hang",
            "Size Option: Customizable up to 48×96\""
        ]
    },
    
    // Acrylic Options
    "Acrylic Face Mount": {
        title: "Acrylic Face Mount Print",
        description: "Your image is face-mounted to crystal-clear acrylic, creating incredible depth and a glass-like finish. Light passes through the acrylic, illuminating your image with stunning brilliance and three-dimensional presence.",
        specs: [
            "Material: 1/4\" premium acrylic",
            "Backing: Dibond aluminum",
            "Finish: Ultra-glossy, glass-like",
            "Mounting: Float mount hardware included",
            "Durability: UV-resistant, easy to clean",
            "Size Option: Customizable up to 48×96\""
        ]
    },
    "Acrylic Print": {
        title: "Direct Acrylic Print",
        description: "Your image is printed directly onto the back of clear acrylic, allowing light to pass through for a vibrant, luminous display with exceptional color saturation.",
        specs: [
            "Material: 1/8\" or 1/4\" acrylic",
            "Finish: High gloss",
            "Mounting: Standoff mounts included",
            "Durability: Scratch-resistant, UV-protected",
            "Vibrancy: Enhanced by light transmission",
            "Size Option: Customizable up to 48×96\""
        ]
    }
};

/**
 * Get description for a substrate option
 * @param {string} optionValue - The substrate option name (e.g., "Hot Press", "Aluminum")
 * @returns {object|null} - Description object or null if not found
 */
function getSubstrateDescription(optionValue) {
    // Clean up the option value to match keys
    const cleanValue = optionValue.replace(/\s*\(.*?\)\s*/g, '').trim();
    
    // Try exact match first
    if (substrateDescriptions[cleanValue]) {
        return substrateDescriptions[cleanValue];
    }
    
    // Try partial match
    for (const key in substrateDescriptions) {
        if (cleanValue.includes(key) || key.includes(cleanValue)) {
            return substrateDescriptions[key];
        }
    }
    
    return null;
}

// Export for use in other scripts
window.getSubstrateDescription = getSubstrateDescription;
