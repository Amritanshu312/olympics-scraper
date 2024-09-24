const express = require('express');
const axios = require('axios');
const cheerio = require('cheerio');
const dotenv = require('dotenv');

// Load environment variables from .env file
dotenv.config();

const app = express();

// Load sensitive data from environment variables
const COOKIE = process.env.OLYMPICS_COOKIE;

// Paris 2024 Olympics Highlights URL
const URL = 'https://olympics.com/en/paris-2024/videos/list/highlights';

// Headers for the request
const HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
    'Cookie': COOKIE,
    'Referer': 'https://olympics.com/en/',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'en-US,en;q=0.8',
};

// Fetch highlights from the Paris 2024 Olympics page
async function fetchHighlights() {
    try {
        const response = await axios.get(URL, { headers: HEADERS });
        return response.data;
    } catch (error) {
        console.error(`Error fetching the page: ${error}`);
        return null;
    }
}

// Parse the highlights from the page content using Cheerio
function parseHighlights(htmlContent) {
    const $ = cheerio.load(htmlContent);
    const highlights = [];

    // Locate the section that contains the videos
    const table = $('section.Grid-styles__GridContainer-sc-57f17f60-0.gaYTef.grid__column--8-xl.min-height-container');

    if (table.length) {
        const rows = table.find('div.AllVideosGroup-styles__CardItemWrapper-sc-676df772-2.fwAJO.all-videos-card-item');
        rows.each((_, row) => {
            const title = $(row).find('h3[data-cy="title"]').text().trim();
            const description = $(row).find('span[data-cy="with-read-more-content"]').text().trim();
            const imageUrl = $(row).find('img').attr('src');
            const videoLink = $(row).find('a[data-cy="link"]').attr('href');

            highlights.push({
                title,
                description,
                image_url: imageUrl,
                video_link: `https://olympics.com${videoLink}`,
            });
        });
    }
    return highlights;
}

// API endpoint to fetch and return highlights
app.get('/api/highlights', async (req, res) => {
    const htmlContent = await fetchHighlights();
    if (!htmlContent) {
        return res.status(500).json({ detail: 'Failed to fetch highlights' });
    }

    const highlights = parseHighlights(htmlContent);
    if (!highlights.length) {
        return res.status(404).json({ detail: 'No highlights found' });
    }

    return res.json(highlights);
});

// Start the Express app
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});
