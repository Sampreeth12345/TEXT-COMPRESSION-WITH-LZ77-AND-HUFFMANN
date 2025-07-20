import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.FileWriter;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;
import java.util.PriorityQueue;
import java.util.Scanner;

public class HuffmanCompression {
    public static void main(String[] args) {
        System.out.println("File Compression Using Huffman Coding".center(100));

        // Get the file path from the user
        String text;
        while (true) {
            System.out.print("Enter the file path: ");
            text = System.console().readLine();
            File file = new File(text);
            if (file.exists()) {
                break;
            } else {
                System.out.println("File not found!");
            }
        }

        displayMessage("Compressing File...", 1000);

        Map<Character, Integer> freqLib = new HashMap<>();
        try (Scanner fileScanner = new Scanner(new File(text))) {
            while (fileScanner.hasNextLine()) {
                String line = fileScanner.nextLine();
                for (char ch : line.toCharArray()) {
                    freqLib.merge(ch, 1, Integer::sum);
                }
            }
        } catch (IOException e) {
            System.out.println("Error reading from file!");
            return;
        }

        PriorityQueue<Node> heap = new PriorityQueue<>();
        freqLib.forEach((symbol, frequency) -> heap.offer(new Node(symbol, frequency)));

        while (heap.size() > 1) {
            Node right = heap.poll();
            Node left = heap.poll();

            right.assignCode('0');
            left.assignCode('1');

            heap.offer(new Node('\0', right.getFrequency() + left.getFrequency(), left, right));
        }

        Node huffmanTree = heap.poll();

        Map<Character, String> huffmanDict = new HashMap<>();
        huffmanTree.buildDictionary(huffmanDict, "");

        StringBuilder encodedText = new StringBuilder();
        try (Scanner fileScanner = new Scanner(new File(text))) {
            while (fileScanner.hasNextLine()) {
                String line = fileScanner.nextLine();
                for (char ch : line.toCharArray()) {
                    encodedText.append(huffmanDict.get(ch));
                }
            }
        } catch (IOException e) {
            System.out.println("Error reading from file!");
            return;
        }

        int padding = 8 - (encodedText.length() % 8);
        StringBuilder paddedEncodedText = new StringBuilder(encodedText);
        paddedEncodedText.append("0".repeat(padding));

        byte[] compressedBytes = new byte[paddedEncodedText.length() / 8];
        for (int i = 0; i < paddedEncodedText.length(); i += 8) {
            String byteStr = paddedEncodedText.substring(i, i + 8);
            byte b = (byte) Integer.parseInt(byteStr, 2);
            compressedBytes[i / 8] = b;
        }

        try (FileOutputStream fos = new FileOutputStream("compressed_file.bin")) {
            fos.write(compressedBytes);
        } catch (IOException e) {
            System.out.println("Error writing to file!");
            return;
        }

        displayMessage("File Successfully Compressed!", 500);

        displayMessage("Decompressing File...", 1000);

        byte[] decompressedBytes;
        try (FileInputStream fis = new FileInputStream("compressed_file.bin")) {
            decompressedBytes = fis.readAllBytes();
        } catch (IOException e) {
            System.out.println("Error reading from file!");
            return;
        }

        StringBuilder decodedText = new StringBuilder();
        for (byte b : decompressedBytes) {
            String byteStr = String.format("%8s", Integer.toBinaryString(b & 0xFF)).replace(' ', '0');
            decodedText.append(byteStr);
        }

        decodedText.setLength(decodedText.length() - padding);

        StringBuilder result = new StringBuilder();
        int idx = 0;
        while (idx < decodedText.length()) {
            Node currentNode = huffmanTree;
            while (!currentNode.isLeaf()) {
                if (decodedText.charAt(idx) == '0') {
                    currentNode = currentNode.getLeftChild();
                } else {
                    currentNode = currentNode.getRightChild();
                }
                idx++;
            }
            result.append(currentNode.getSymbol());
        }

        displayMessage("File Successfully Decompressed!", 500);
        System.out.println("Decompressed text is: " + result.toString());

        try (FileWriter fw = new FileWriter("decompressed.txt")) {
            fw.write(result.toString());
        } catch (IOException e) {
            System.out.println("Error writing to file!");
            return;
        }
    }

    private static void displayMessage(String message, long duration) {
        System.out.println(message);
        try {
            Thread.sleep(duration);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }

    static class Node implements Comparable<Node> {
        private final char symbol;
        private final int frequency;
        private String code;
        private final Node leftChild;
        private final Node rightChild;

        public Node(char symbol, int frequency) {
            this(symbol, frequency, null, null);
        }

        public Node(char symbol, int frequency, Node leftChild, Node rightChild) {
            this.symbol = symbol;
            this.frequency = frequency;
            this.leftChild = leftChild;
            this.rightChild = rightChild;
        }

        public char getSymbol() {
            return symbol;
        }

        public int getFrequency() {
            return frequency;
        }

        public String getCode() {
            return code;
        }

        public void assignCode(char c) {
            code = c + code;
            if (leftChild != null) {
                leftChild.assignCode(c);
            }
            if (rightChild != null) {
                rightChild.assignCode(c);
            }
        }

        public boolean isLeaf() {
            return leftChild == null && rightChild == null;
        }

        public Node getLeftChild() {
            return leftChild;
        }

        public Node getRightChild() {
            return rightChild;
        }

        public void buildDictionary(Map<Character, String> dictionary, String prefix) {
            if (isLeaf()) {
                dictionary.put(symbol, prefix);
            }
            if (leftChild != null) {
                leftChild.buildDictionary(dictionary, prefix + "1");
            }
            if (rightChild != null) {
                rightChild.buildDictionary(dictionary, prefix + "0");
            }
        }

        @Override
        public int compareTo(Node other) {
            return Integer.compare(this.frequency, other.frequency);
        }
    }
}
