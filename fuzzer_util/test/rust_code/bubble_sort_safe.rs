pub fn swap(arr: &mut [i32], i: usize, j: usize) {
    let temp = arr[i];
    arr[i] = arr[j];
    arr[j] = temp;
}

pub fn bubble_sort(arr: &mut [i32]) {
    let size = arr.len();
    for i in 0..size {
        for j in 0..size - 1 - i {
            if arr[j] > arr[j + 1] {
                swap(arr, j, j + 1);
            }
        }
    }
}

static N: usize = 97;

pub fn create_array_from_args(args: Vec<String>) -> Result<Vec<i32>, &'static str> {
    if args.len() != N + 1 {
        return Err("Error: Expected 97 arguments, but got fewer.");
    }
    let mut arr: Vec<i32> = vec![0; N];
    for i in 0..N {
        arr[i] = args.get(i+1)
                    .ok_or("No argument found for this index.")?
                    .parse::<i32>()
                    .or(Err("Failed to parse argument to integer."))?;
    }
    Ok(arr)
}

fn main() {
    let args: Vec<String> = std::env::args().collect();

    if args.len() != N + 1 {
        eprintln!("Error: Expected 97 arguments, but got {}.", args.len()-1);
        return;
    }

    let mut numbers = match create_array_from_args(args) {
        Ok(numbers) => numbers,
        Err(err) => {
            eprintln!("{}", err);
            return;
        },
    };

    let size = 10000;
    for _ in 0..size {
        bubble_sort(&mut numbers);
    }

    for i in 0..N {
        print!("{} ", numbers[i]);
    }

    println!("");
}