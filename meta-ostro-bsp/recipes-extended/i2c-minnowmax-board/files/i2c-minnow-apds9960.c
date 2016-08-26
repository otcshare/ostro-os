/*
 * MinnowBoard-Max APDS9960 I2C sensor test file
 * build command: KDIR=/kernel-source/ make
 * The kernel config should include CONFIG_APDS9960=m
 */

#include <linux/module.h>
#include <linux/gpio.h>
#include <linux/i2c.h>

#define APDS9960_I2C_ADDR		0x39

/* The APDS9960 IRQ pin is connected to pin25(GPIO_S5_2) of LSE connector,
 * On Linux >=3.18, it is GPIO 340
 * For more information, visit the below
 * http://www.elinux.org/Minnowboard:MinnowMax#Low_Speed_Expansion_.28Top.29
 */
#define APDS9960_I2C_IRQ		340

static struct i2c_board_info apds9960_accel_device = {
	I2C_BOARD_INFO("apds9960", APDS9960_I2C_ADDR),
	.irq = -1,
};

static struct i2c_client *i2c_client;
static int __init apds9960_init(void)
{
	int i = 0;
	struct i2c_adapter *adap = NULL;

	for (i = 0; i < 3; i++) {
		adap = i2c_get_adapter(i);
		if (!adap)
			return -1;

		if (!strcmp(adap->name, "Synopsys DesignWare I2C adapter"))
			break;
	}

	apds9960_accel_device.irq = gpio_to_irq(APDS9960_I2C_IRQ);

	i2c_client = i2c_new_device(adap, &apds9960_accel_device);
	return 0;
}

static void __exit apds9960_exit(void)
{
	i2c_unregister_device(i2c_client);
}
MODULE_LICENSE("GPL");
module_init(apds9960_init);
module_exit(apds9960_exit);
