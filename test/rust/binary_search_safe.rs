use pyo3::prelude::*;

pub fn binarysearch2(arr: &[i32], l: usize, r: usize, x: i32) -> i32 {
    let mut l = l;
    let mut r = r;
    while l < r {
        let m = l + (r - l) / 2;

        if arr[m] == x {
            return m as i32;
        }

        if arr[m] < x {
            l = m + 1;
        } else {
            if l == m {
              break;
            }
            r = m;
        }
    }
    -1
}

const N: usize = 97;

pub fn create_array_from_args(args: Vec<i32>) -> Box<[i32]> {
    args.into_boxed_slice()
}

pub fn validate_arg_count(argc: usize, expected_argc: usize) {
    if argc != expected_argc {
        println!("Error: Expected {} arguments, but got {}.", expected_argc, argc);
        std::process::exit(1);
    }
}

#[pyfunction]
pub fn main_py(args: Vec<i32>) {
    let args: Vec<i32> = std::env::args()
        .skip(1)
        .map(|s| s.parse().unwrap())
        .collect();

    validate_arg_count(args.len(), N);

    let numbers = create_array_from_args(args);

    let mut k = 0;

    for _ in 0..3000000 {
        k = binarysearch2(&numbers, 0, N-1, 284);
    }

    println!("{}", k);
}

