
// struct TextFile {}

// struct CSVFile {}

// use std::fs::File; 

let FilePath = "path/to/textfile.txt";
let FILE = std::fs::File::open();

fn main() {
    let sentence = "Convert Text to ASCII: \nValue1".lines();

    // Protofunction (For loop to iterate through "linelines")
    // TODO: 
    for (index, value) in sentence.enumerate() {
        println!("Line {}: {}", index, value);
    }
}
