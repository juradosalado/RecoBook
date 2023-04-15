console.log('Sanity check!')
document.addEventListener('DOMContentLoaded', function() {
    const button = document.querySelector('.read-more-btn');
    const description = document.querySelector('.description-div');

    const maxLength = 200; // Set the maximum length of the description

    // Get the full text of the description
    const fullText = description.innerHTML.trim();

    const startIndex = fullText.indexOf('</strong>') + '</strong>'.length;
    const titleText = fullText.substring(0, startIndex);
    const descriptionText = fullText.substring(startIndex);

    

    // Truncate the text to the maximum length
    const truncatedText = descriptionText.slice(0, maxLength) + '...';

    // Replace the text in the description with the truncated text
    description.innerHTML = titleText + truncatedText;

    // Show the "Read More" button
    button.style.display = 'inline-block';

    // Add an event listener to the "Read More" button
    button.addEventListener('click', () => {
      // Check if the description is currently truncated
      const isTruncated = description.textContent.trim().endsWith('...');

      // Update the text on the button
      if(description.textContent.trim().endsWith('...')){
        button.textContent = 'Read Less';
      }else{
        button.textContent = 'Read More';
      }
      
      // Toggle the text between the full text and the truncated text
      description.innerHTML = isTruncated ? fullText : titleText + truncatedText;
      
    });

  });
