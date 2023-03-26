console.log('Sanity check!')
document.addEventListener('DOMContentLoaded', function() {
    const button = document.querySelector('.read-more');
const description = document.querySelector('.description-div');

const maxLength = 200; // Set the maximum length of the description

// Get the full text of the description
const fullText = description.textContent.trim();

// Truncate the text to the maximum length
const truncatedText = fullText.slice(0, maxLength) + '...';

// Replace the text in the description with the truncated text
description.textContent = truncatedText;

// Show the "Read More" button
button.style.display = 'inline-block';

// Add an event listener to the "Read More" button
button.addEventListener('click', () => {
  // Check if the description is currently truncated
  const isTruncated = description.textContent.trim().endsWith('...');
  
  // Toggle the text between the full text and the truncated text
  description.textContent = isTruncated ? fullText : truncatedText;
  
  // Update the text on the button
  button.textContent = isTruncated ? 'Read More' : 'Read Less';
});

  });
