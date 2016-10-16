makeCacheMatrix <- function(martixCache = matrix()) {
	inverseCache <- NULL

	# Cache the original matrix and set the cached matrix to NULL
    set <- function(original) {
        martixCache  <<- original
		inverseCache <<- NULL
	}

	# Return the original matrix
	get <- function() {
	    matrixCache
    }

	# Cache the inverse of the matrix
    setInverse <- function(inverse) {
        inverseCache <<- inverse
    }

	# Return the cached inverse of the matrix
    getInverse <- function() {
        inverseCache
    }

    list(set = set,
         get = get,
         setInverse = setInverse,
         getInverse = getInverse)
}

cacheSolve <- function(x, ...) {
    # Get the cached inverse of the matrix
    inverse <- x$getInverse()

	# Check if the inverse is NULL
    if(!is.null(inverse)) {
        message("Getting cached inverse")
        return(inverse)
    }

	# Getting the issued matrix
    data <- x$get()

	# Solve the inverse of the matrix
    inverse <- solve(data, ...)

	# Cache the inverse of the matrix
    x$setInverse(inverse)

	# Return the inverse of the matrix
    inverse
}
