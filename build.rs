use cxx_qt_build::CxxQtBuilder;

fn main() {
    CxxQtBuilder::new()
        .file("src/qt/main_window.rs") // Specify the Rust file with #[cxx_qt::bridge]
        .build();
}