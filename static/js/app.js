// https://openlibrary.org/search.json?q=harry%20potter&_facet=false&_spellcheck_count=0&limit=10&fields=key,cover_i,title,author_name,name&mode=everything

const OPEN_LIB_URL = 'https://openlibrary.org';
const COVERS_URL = 'https://covers.openlibrary.org/b/id/';
const SERVER_URL = 'http://127.0.0.1:5000';

$('#search-form').on('submit', async function(evt) {
	evt.preventDefault();

	$('#results-list').empty();

	const subject = $('#subject').val();
	const query = $('#search').val();
	let parameters = {};

	if (subject === 'title') {
		parameters = {
			q: query,
			limit: 10,
			fields: 'key,cover_i,title,author_name,name,seed',
			mode: 'everything'
		};
	} else {
		parameters = {
			author: query,
			limit: 10,
			fields: 'key,cover_i,title,author_name,name,seed',
			mode: 'everything'
		};
	}
	const res = await axios.get(`${OPEN_LIB_URL}/search.json`, {
		params: parameters
	});

	for (let bookData of res.data.docs) {
		book = $(generateBook(bookData));
		$('#results-list').append(book);
	}
});

function generateBook(book) {
	// Use the first seed for bookID, this way it will correspond to the bookdata and have details for the ISBN
	const bookID = book['seed'][0].slice(7);

	return `<div class="book-tag" data-id=${bookID}> <img src="${COVERS_URL}${book[
		'cover_i'
	]}-M/jpg" alt="No image available" class="cover-image"> <li> Title: ${book['title']} </li> <li> Author: ${book[
		'author_name'
	][0]} </li> </div>`;
}

// TODO: Use event delegation on #results-list in order to create listener function on each child div. The function should send a post query to the server that uses the book[key] to pull more info about the book from the Works API, transforms the result into a BookTalk object, and then renders a new page displaying that object. This object can then be added to the BookTalk database IF another book with a matching title and author does not already exist

$('#results-list').on('click', '.book-tag', async function(evt) {
	// Get data from parent div regardless on what element was clicked on
	const $bookData = $(evt.target).closest('div')[0];

	// Get the URL for the works request
	const bookID = $bookData.dataset.id;

	// Post the URL to the add book route on the server where it will be sent and then transformed into a BookTalk object, and then redirect to a new page where the book object can be added to the database
	const res = await axios.post(`${SERVER_URL}/books/show`, { bookID });
});
