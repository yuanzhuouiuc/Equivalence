pub fn swap(first: &mut i32, second: &mut i32) {
    let temp = *first;
    *first = *second;
    *second = temp;
}

pub fn bubble_sort(arr: &mut Vec<i32>, size: usize) {
    for i in 0..size - 1 {
        for j in 0..size - 1 - i {
            if arr[j] > arr[j + 1] {
                swap(&mut arr[j], &mut arr[j + 1]);
            }
        }
    }
}

let n = 97;

pub fn create_array_from_args(args: Vec<String>, size: &mut usize) -> Vec<i32> {
    *size = args.len() - 1;
    let mut arr: Vec<i32> = vec![0; *size];
    for i in 0..*size {
        arr[i] = args.get(i+1)
                     .expect("No argument found for this index.")
                     .parse()
                     .expect("Failed to parse argument to integer.");
    }
    arr
}

pub fn validate_arg_count(args: Vec<String>, expected_argc: usize) {
    let argc = args.len() - 1;
    if argc != expected_argc {
        panic!("Error: Expected {} arguments, but got {}.", expected_argc, argc);
    }
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    validate_arg_count(args.clone(), n);

    let mut numbers: Vec<i32> = create_array_from_args(args.clone(), &mut n);

    let size = 1;

    for _ in 0..size {
        bubble_sort(&mut numbers, n);
    }

    for i in 0..n {
        print!("{} ", numbers[i]);
    }
    println!("");
}