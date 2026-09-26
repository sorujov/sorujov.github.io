for N in "$@"; do bash render.sh $N h > r$N.out 2>&1; done
