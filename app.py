// Replace the func: () => { ... } section in your popup.js
func: () => {
    const items = [];
    // We search for ANY element that contains a currency symbol
    const elements = document.querySelectorAll('div, li, span');
    
    elements.forEach(el => {
        // Look for the specific Indian Rupee symbol or 'Rs'
        const text = el.innerText;
        const priceMatch = text.match(/(?:₹|Rs\.?|INR)\s?([\d,]+(?:\.\d{2})?)/);
        
        if (priceMatch && text.length < 200) {
            // Find the closest parent that might have the name
            // Or just take the first part of the text
            let name = text.split(/[₹|Rs|INR]/)[0].trim();
            if (name.length < 5) return; // Skip if it's just a random number

            items.push({
                name: name.substring(0, 50),
                price: parseInt(priceMatch[1].replace(/,/g, '')),
                site: window.location.hostname
            });
        }
    });
    
    // Remove duplicates (since we might grab the same price from parent and child)
    return items.filter((v, i, a) => a.findIndex(t => (t.name === v.name)) === i);
}
