# src/catalogue
*Book* is a title the bookshop sells: it holds the title's price and the copies in stock, and answers whether a copy can be sold.

*Catalogue* is the shelf a customer browses: it finds books by a search word and hands out a *Book* by its ISBN.

- **Purpose:** let a customer browse the books the shop sells and learn each one's price and stock
- **Seam (terms):** Book, Catalogue
- **Dependencies (one-way):** none

## Constraint

Take stock only through `Book.reserve`; a caller never writes the number of copies itself.
