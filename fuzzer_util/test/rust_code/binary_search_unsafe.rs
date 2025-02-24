pub fn binarysearch2(arr: &[i32], l: usize, r: usize, x: i32) -> i32 {
    let mut l = l;
    let mut r = r;
    while l <= r {
        let m = l + (r - l) / 2;

        if arr[m] == x {
            return m as i32;
        }

        if arr[m] < x {
            l = m + 1;
        } else {
            r = m - 1;
        }
    }
    -1
}

const N: usize = 97;

pub fn create_array_from_args(args: Vec<i32>) -> Box<[i32]> {
    let size = args.len();
    let arr = Box::new(*args);

    let mut res = vec![0; size];
    for i in 0..size {
        res[i] = arr[i];
    }

    res.into_boxed_slice()
}

pub fn validate_arg_count(argc: usize, expected_argc: usize) {
    if argc - 1 != expected_argc {
        println!("Error: Expected {} arguments, but got {}.", expected_argc, argc - 1);
        std::process::exit(1);
    }
}

pub fn main(args: Vec<i32>) {
    validate_arg_count(args.len(), N);

    let numbers = create_array_from_args(args);

    let mut k = 0;

    for _ in 0..3 {
        k = binarysearch2(&numbers, 0, N, 284);
    }

    println!("{}", k);
}


