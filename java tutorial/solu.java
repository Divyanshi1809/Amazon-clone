
import java.io.*;
import java.time.*;
import java.time.format.*;

public class solu {

    public static String findDay(int month, int day, int year) {
        // Create a LocalDate instance for the given year, month, and day
        LocalDate date = LocalDate.of(year, month, day);
        
        // Get the day of the week in capital letters
        return date.getDayOfWeek().toString();
    }

    public static void main(String[] args) throws IOException {
        // BufferedReader is used to read input from the user
        BufferedReader bufferedReader = new BufferedReader(new InputStreamReader(System.in));

        // Reading input (month, day, year)
        String[] input = bufferedReader.readLine().split(" ");
        int month = Integer.parseInt(input[0]);
        int day = Integer.parseInt(input[1]);
        int year = Integer.parseInt(input[2]);

        // Find the day of the week for the given date
        String dayOfWeek = findDay(month, day, year);

        // Print the result
        System.out.println(dayOfWeek);

        bufferedReader.close();
    }
}

