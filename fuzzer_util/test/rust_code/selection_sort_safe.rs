use std::env;
use std::process;

pub fn swap(arr: &mut [i32], a: usize, b: usize) {
    let temp = arr[a];
    arr[a] = arr[b];
    arr[b] = temp;
}

pub fn selection_sort(arr: &mut [i32], size: usize) {
    for i in 0..size - 1 {
        let mut min_index = i;
        for j in i + 1..size {
            if arr[j] < arr[min_index] {
                min_index = j;
            } 
        }
        if min_index != i {
            swap(arr, i, min_index);
        }
    } 
}

pub fn validate_arg_count(argc: usize, expected_argc: i32) {
    if (argc - 1) as i32 != expected_argc {
        eprintln!("Error: Expected {} arguments, but got {}.", expected_argc, argc - 1);
        process::exit(1);
    } 
}

fn main() {
    let args: Vec<String> = env::args().collect();
    let argc = args.len();
    let n = 97;

    validate_arg_count(argc, n);

    let mut numbers: Vec<i32> = Vec::new();
    for i in 1..argc {
        numbers.push(args[i].parse().unwrap());
    } 

    let size = 10000;

    for _i in 0..size {
        selection_sort(&mut numbers[..], n as usize);
    } 

    for i in 0..n {
        print!("{} ", numbers[i as usize]);
    } 

    println!();
}