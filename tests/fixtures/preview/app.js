let count = 0;
document.querySelector('#increment').onclick = () => { document.querySelector('#count').textContent = ++count; };
document.querySelector('#form').onsubmit = event => { event.preventDefault(); document.querySelector('#output').textContent = document.querySelector('#name').value; };
document.querySelector('#error').onclick = () => { throw new Error('WishCode fixture error'); };
