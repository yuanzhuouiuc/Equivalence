use std::env;
use std::process;

pub fn reverse(s: &mut [char]) {
    let (mut i, mut j) = (0, s.len() - 1);
    while i < j {
        let c = s[i];
        s[i] = s[j];
        s[j] = c;
        i += 1;
        j -= 1;
    }
}

pub fn create_array_from_args(args: Vec<String>) -> Vec<char> {
    let args: Vec<_> = args.into_iter().filter(|arg| arg.len() == 1).collect();
    if args.len() != 306 {
        eprintln!("Error: Expected 306 single character arguments.");
        process::exit(1);
    }
    args.iter().map(|arg| arg.chars().next().unwrap()).collect()
}

pub fn validate_arg_count(argc: usize, expected_argc: usize) {
    if argc != expected_argc {
        eprintln!(
            "Error: Expected {} arguments, but got {}.",
            expected_argc, argc
        );
        process::exit(1);
    }
}

pub fn main() {
    let args: Vec<String> = env::args().skip(1).collect();
    validate_arg_count(args.len(), 306);
    let mut numbers = create_array_from_args(args);
    for _ in 0..10000 {
        reverse(&mut numbers);
    }
    for number in &numbers {
        print!("{} ", number);
    }
    println!();
}
