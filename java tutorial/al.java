
import java.util.Scanner;
import java.util.ArrayList;
public class al {
    public static void main(String[] args) {
        Scanner scan=new Scanner(System.in);

        ArrayList<ArrayList<Integer>> list=new ArrayList<>();

        //intilaisation
        for (int i=0;i<3;i++){
            list.add(new ArrayList<>());
        }
        for (int i=0;i<3;i++){
            for(int j=0;j<3;j++){
                list.get(i).add(scan.nextInt());
            }
        }
        System.out.println(list);
    }
}
